use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Debug, Clone)]
pub struct ClusterNode {
    pub node_id: String,
    pub address: String,
    pub is_active: bool,
}

#[derive(Debug)]
pub enum HealthStatus {
    Healthy,
    Degraded(String),
    Offline,
}

pub trait NodeEvaluator {
    fn check_health(&self) -> HealthStatus;
}

impl NodeEvaluator for ClusterNode {
    fn check_health(&self) -> HealthStatus {
        if self.is_active {
            HealthStatus::Healthy
        } else {
            HealthStatus::Offline
        }
    }
}

pub async fn run_monitoring_engine(node: Arc<Mutex<ClusterNode>>) {
    let locked = node.lock().await;
    println!("Inspecting node: {}", locked.node_id);
}
