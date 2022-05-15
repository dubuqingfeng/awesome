package main

import (
	"context"
	"fmt"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	// 当我们取完需要的整数后调用cancel
	defer cancel()

	// 从通道中读出
	for n := range gen(ctx) {
		fmt.Println(n)
		if n == 5 {
			break
		}
	}
}

func gen(ctx context.Context) <-chan int {
	dst := make(chan int)
	n := 1
	go func() {
		for {
			select {
			// 用context结束掉，其实就是读取到空的struct
			case <-ctx.Done():
				fmt.Println("done")
				return // return结束该goroutine，防止泄露
			case dst <- n:
				n++
			}
		}
	}()
	return dst
}
