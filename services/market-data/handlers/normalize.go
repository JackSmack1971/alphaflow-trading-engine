package handlers

import "encoding/json"

func Normalize(input []byte) ([]byte, error) {
	var v map[string]interface{}
	if err := json.Unmarshal(input, &v); err != nil {
		return nil, err
	}
	return json.Marshal(v)
}
