package main

import (
	"fmt"
	"unsafe"
)

type SliceHeader struct {
	Data uintptr
	Len  int
	Cap  int
}

func main() {
	a := []byte{}
	b := []byte{}
	c := [0]int{}
	fmt.Println((*SliceHeader)(unsafe.Pointer(&a)))
	fmt.Println((*SliceHeader)(unsafe.Pointer(&b)))
	fmt.Println(uintptr(unsafe.Pointer(&c)))
}
