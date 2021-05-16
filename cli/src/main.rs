use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use anyhow::Result;
use structopt::StructOpt;
use reqwest;

#[derive(Debug, StructOpt)]
#[structopt(name = "Cowin Notifier", about = "CLI to sign up for covid vaccine alerts")]
enum Opt {
    #[structopt(about = "Register yourself to receive vaccine alerts")]
    Register {
        #[structopt(help = "Enter your state")]
        #[structopt(short, long)]
        state: String,

        #[structopt(help = "Enter your district")]
        #[structopt(short, long)]
        district: String,

        #[structopt(help = "Enter your email")]
        #[structopt(short, long)]
        email: String,
    },

    #[structopt(about = "Verify yourself to start receiving vaccine alerts")]
    Verify {
        #[structopt(help = "Enter your email")]
        #[structopt(short, long)]
        email: String,
        #[structopt(help = "Enter the code sent to your mail")]
        #[structopt(short, long)]
        code: String
    }
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StatesResponse {
    pub states: Vec<State>,
    pub ttl: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct State {
    pub state_id: i64,
    pub state_name: String,
}


#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DistrictsResponse {
    pub districts: Vec<District>,
    pub ttl: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct District {
    pub district_id: i64,
    pub district_name: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct JsonBody {
    pub district: i64,
    pub email: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    let opt = Opt::from_args();
    let base_url = "http://34.93.10.131";
    match opt {
        Opt::Register{state, district, email} => {
            let client = reqwest::Client::builder()
                .user_agent("Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0")
                .build()?;
            let states: StatesResponse = client
                .get("https://cdn-api.co-vin.in/api/v2/admin/location/states")
                .send()
                .await?
                .json::<StatesResponse>()
                .await?;
            let mut state_id = None;
            for state_obj in &states.states {
                if state_obj.state_name == state {
                    state_id = Some(state_obj.state_id);
                }
            }
            if let Some(state_id) = state_id {
                println!("State ID: {}", &state_id);
                let disticts_response = client
                    .get(format!(
                        "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}",
                        state_id
                    ))
                    .send()
                    .await?
                    .json::<DistrictsResponse>()
                    .await?;
                let mut district_id = None;  
                for district_obj in &disticts_response.districts {
                    if district_obj.district_name == district {
                        district_id = Some(district_obj.district_id);
                    }
                }
                if let Some(district) = district_id {
                    let body = JsonBody{
                        district,
                        email
                    };
                    let response = reqwest::Client::new()
                        .post(format!("{}/users/register", base_url))
                        .json(&body)
                        .send()
                        .await?;
                        if response.status() == 201 {
                            println!("Please check your mail and verify yourself with the code provided.");
                        } else {
                            println!("Failed to register you. Please try again.");
                        }
                    }
                }
            return Ok(())
        }
        Opt::Verify{email, code} => {
            let mut body = HashMap::new();
            body.insert("email", email);
            body.insert("code", code);
            let response = reqwest::Client::new()
                .post(format!("{}/users/verify", base_url))
                .json(&body)
                .send()
                .await?;
                if response.status() == 200 {
                    println!("You have been verified. We will send you an email as soon as a vaccination slot opens up in your district");
                } else if response.status() == 401 {
                    println!("Your code seems to be wrong.");
                } else {
                    println!("Somethng went wrong, please try again.");
                }
            return Ok(())
        }
    }
}
