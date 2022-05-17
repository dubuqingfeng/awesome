package main

func main() {
	// channel
	example()
}

func example() {
	ch := make(chan int)
	go func() {
		ch <- 1
		ch <- 2
		ch <- 3
		close(ch)
	}()
	for v := range ch {
		println(v)
	}
}
