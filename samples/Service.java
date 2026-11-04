package com.cloudsphere.analytics;

import java.util.Map;
import java.util.HashMap;

public class Service {
    private final String serviceId;

    public Service(String serviceId) {
        this.serviceId = serviceId;
    }

    public Map<String, Object> getServiceHealth() {
        Map<String, Object> health = new HashMap<>();
        health.put("serviceId", this.serviceId);
        health.put("status", "UP");
        return health;
    }
}
