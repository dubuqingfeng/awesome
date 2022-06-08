package main

import (
	"crypto/sha256"
)

// Shad Double Sha256 Hash; sha256(sha256(data))
func Shad(data []byte) []byte {
	h1 := sha256.Sum256(data)
	h2 := sha256.Sum256(h1[:])
	return h2[:]
}

func main() {
	data := []byte("hello world")
	h := Shad(data)
	println(h)
}