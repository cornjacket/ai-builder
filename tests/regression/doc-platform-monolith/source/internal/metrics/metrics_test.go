package metrics_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	metrics "github.com/cornjacket/platform/internal/metrics"
)

func TestNew_NonNil(t *testing.T) {
	h := metrics.New()
	if h == nil {
		t.Fatal("New() returned nil")
	}
}

func TestPostEvents_ValidBody_Returns201(t *testing.T) {
	h := metrics.New()
	body := `{"type":"click-mouse","userId":"u1","payload":{"k":"v"}}`
	req := httptest.NewRequest(http.MethodPost, "/events", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	h.ServeHTTP(w, req)

	if w.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d", w.Code)
	}

	var resp map[string]interface{}
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	id, ok := resp["id"].(string)
	if !ok || id == "" {
		t.Fatalf("expected non-empty id, got %v", resp["id"])
	}
}

func TestPostEvents_UnknownType_Returns400(t *testing.T) {
	h := metrics.New()
	body := `{"type":"unknown-type","userId":"u1"}`
	req := httptest.NewRequest(http.MethodPost, "/events", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	h.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d", w.Code)
	}
}

func TestGetEvents_Returns200AndArray(t *testing.T) {
	h := metrics.New()
	req := httptest.NewRequest(http.MethodGet, "/events", nil)
	w := httptest.NewRecorder()
	h.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}

	var resp []interface{}
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
}

func TestPostThenGet_EventAppearsInList(t *testing.T) {
	h := metrics.New()

	body := `{"type":"submit-form","userId":"u2","payload":{"form":"login"}}`
	postReq := httptest.NewRequest(http.MethodPost, "/events", bytes.NewBufferString(body))
	postReq.Header.Set("Content-Type", "application/json")
	postW := httptest.NewRecorder()
	h.ServeHTTP(postW, postReq)
	if postW.Code != http.StatusCreated {
		t.Fatalf("POST: expected 201, got %d", postW.Code)
	}

	var postResp map[string]interface{}
	json.NewDecoder(postW.Body).Decode(&postResp)
	postedID := postResp["id"].(string)

	getReq := httptest.NewRequest(http.MethodGet, "/events", nil)
	getW := httptest.NewRecorder()
	h.ServeHTTP(getW, getReq)
	if getW.Code != http.StatusOK {
		t.Fatalf("GET: expected 200, got %d", getW.Code)
	}

	var events []map[string]interface{}
	json.NewDecoder(getW.Body).Decode(&events)
	for _, ev := range events {
		if ev["id"] == postedID {
			return
		}
	}
	t.Fatalf("posted event %q not found in GET /events response", postedID)
}
