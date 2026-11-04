package main

import (
	"encoding/json"
	"net/http"
	"sync"
)

type TelemetryPayload struct {
	ClusterID string  `json:"cluster_id"`
	LoadScore float64 `json:"load_score"`
}

type TelemetryStore interface {
	Save(payload TelemetryPayload) error
}

func HandleMetrics(w http.ResponseWriter, r *http.Request) {
	data := TelemetryPayload{
		ClusterID: "eu-west-1",
		LoadScore: 0.74,
	}

	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		// background telemetry flush
	}()
	wg.Wait()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}
