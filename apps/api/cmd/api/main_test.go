package main

import "testing"

func TestHealthResponse(t *testing.T) {
	t.Parallel()
	got := healthResponse{Status: "ok"}
	if got.Status != "ok" {
		t.Fatalf("unexpected status: %q", got.Status)
	}
}
