package main

import (
	"fmt"
)

func main() {
	var intArr = []int{14, 41, 12, 23, 19, 7, 42, 31, 44, 21, 11, 43, 30, 10, 24, 18, 6, 22, 17, 5, 20, 16, 4, 15, 3, 13, 2, 1}
	chOdd := make(chan int)
	chEven := make(chan int)

	go odd(chOdd)
	go even(chEven)

	for _, value := range intArr {
		if value%2 != 0 {
			chOdd <- value
		} else {
			chEven <- value
		}
	}
}

func odd(ch <-chan int) {
	for v := range ch {
		fmt.Println("ODD :", v)
	}
}

func even(ch <-chan int) {
	for v := range ch {
		fmt.Println("EVEN:", v)
	}
}
