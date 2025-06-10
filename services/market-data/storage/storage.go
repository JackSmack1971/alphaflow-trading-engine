package storage

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
)

type Store struct {
	db *sql.DB
}

func (s *Store) DB() *sql.DB { return s.db }

func New(path string) (*Store, error) {
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, err
	}
	if _, err := db.Exec(`CREATE TABLE IF NOT EXISTS ticks(id INTEGER PRIMARY KEY AUTOINCREMENT,symbol TEXT,data TEXT,ts DATETIME DEFAULT CURRENT_TIMESTAMP)`); err != nil {
		return nil, err
	}
	return &Store{db: db}, nil
}

func (s *Store) Save(symbol string, data []byte) error {
	_, err := s.db.Exec(`INSERT INTO ticks(symbol,data) VALUES(?,?)`, symbol, string(data))
	return err
}

func (s *Store) History(symbol string, limit int) ([][]byte, error) {
	rows, err := s.db.Query(`SELECT data FROM ticks WHERE symbol=? ORDER BY id DESC LIMIT ?`, symbol, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var res [][]byte
	for rows.Next() {
		var d string
		if err := rows.Scan(&d); err != nil {
			return nil, err
		}
		res = append(res, []byte(d))
	}
	return res, nil
}
