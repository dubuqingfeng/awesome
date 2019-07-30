package main

import "fmt"

var quit chan int
var glo int

func test() {
    fmt.Println(glo)
}

func main() {
    glo = 0
    n := 10000
    quit = make(chan int, n)
    go test()
    for {
        quit <- 1
        glo++
    }
}
