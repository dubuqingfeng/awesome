package main

import (
	"crypto/sha512"
	"encoding/base64"
	"encoding/csv"
	"fmt"
	"io/ioutil"
	"strings"

	"golang.org/x/crypto/bcrypt"
	"golang.org/x/crypto/pbkdf2"
)

type TestCase struct {
	password         string
	salt             string
	expectedPassword string
}

func main() {
	file, err := ioutil.ReadFile("test.csv")
	if err != nil {
		panic(err)
	}
	reader := csv.NewReader(strings.NewReader(string(file)))
	rows, _ := reader.ReadAll()
	count := len(rows)
	for i := 0; i < count; i++ {
		password := rows[i][0]
		salt := rows[i][1]
		salt1, err := base64.StdEncoding.DecodeString(salt)
		if err != nil {
			fmt.Println(err)
		}
		result := pbkdf2.Key([]byte(password), salt1, 35000, 32, sha512.New)
		if err := bcrypt.CompareHashAndPassword([]byte(rows[i][2]), result); err != nil {
			fmt.Println(err)
			fmt.Println(password)
			fmt.Println(salt)
		}
	}
}
