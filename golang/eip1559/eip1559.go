package main

import (
	"fmt"
	"math/big"
	"os"
	"os/signal"
	"sync"
	"time"
)

var tick <-chan time.Time
var isclose bool
var ch chan bool

func handle() {
	for {
		select {
		case <-tick:
			fmt.Println("tick.", time.Now().UTC())
		case <-ch:
			fmt.Println("1221313")
			close(ch)
			return
			// default:
			// 	if isclose {
			// 		fmt.Println("1121212")
			// 		return
			// 	}
			// fmt.Println(".")
		}
	}
}

func run() {
	var wg sync.WaitGroup
	defer func() {
		wg.Wait()
	}()
	isclose = false
	ch = make(chan bool, 1)
	tick = time.Tick(1 * time.Millisecond)
	interruptCh := make(chan os.Signal, 1)
	signal.Notify(interruptCh, os.Interrupt)
	wg.Add(1)
	go func() {
		handle()
		wg.Done()
	}()
	for {
		select {
		case <-interruptCh:
			fmt.Println("12345")
			isclose = true
			ch <- true
			return
		}
	}
}

func cal() {
	var gaslimit, gasUsed, baseFee uint64
	gaslimit = 14834603
	gasUsed = 11078018
	baseFee = 990148730
	// (11078018 - (14834603 / 2)) * 990148730 / (14834603 / 2) / 8
	// (11078018 - (14834603 / 2)) * 990148730 / 7417301 / 8
	// 3660717
	var (
		parentGasTarget          = gaslimit / 2
		parentGasTargetBig       = new(big.Int).SetUint64(parentGasTarget)
		baseFeeChangeDenominator = new(big.Int).SetUint64(8)
	)
	fmt.Printf("parentGasTarget: %d\n", parentGasTarget)
	baseFeeBig := new(big.Int).SetUint64(baseFee)
	// If the parent gasUsed is the same as the target, the baseFee remains unchanged.
	if gasUsed == parentGasTarget {
		fmt.Println(new(big.Int).Set(baseFeeBig))
	}
	if gasUsed > parentGasTarget {
		// If the parent block used more gas than its target, the baseFee should increase.
		gasUsedDelta := new(big.Int).SetUint64(gasUsed - parentGasTarget)
		fmt.Printf("gasUsedDelta: %d\n", gasUsedDelta)
		x := new(big.Int).Mul(baseFeeBig, gasUsedDelta)
		fmt.Printf("x: %d\n", x)
		fmt.Printf("parentGasTargetBig: %d\n", parentGasTargetBig)
		y := x.Div(x, parentGasTargetBig)
		fmt.Printf("y: %d\n", y)
		fmt.Printf("x: %d\n", x)
		baseFeeDelta := x.Div(y, baseFeeChangeDenominator)
		fmt.Println(baseFeeDelta)
		fmt.Println(x.Add(baseFeeBig, baseFeeDelta))
	} else {
		// Otherwise if the parent block used less gas than its target, the baseFee should decrease.
		gasUsedDelta := new(big.Int).SetUint64(parentGasTarget - gasUsed)
		x := new(big.Int).Mul(baseFeeBig, gasUsedDelta)
		y := x.Div(x, parentGasTargetBig)
		baseFeeDelta := x.Div(y, baseFeeChangeDenominator)
		fmt.Println(x.Sub(baseFeeBig, baseFeeDelta))
	}
}

func main() {
	cal()
	// go func() {
	// 	run()
	// }()
	// err := http.ListenAndServe("0.0.0.0:6060", nil)
	// fmt.Println(err)
	// _, _ = profiler.Start(profiler.Config{
	// 	// TODO: add SampleRate, https://github.com/pyroscope-io/pyroscope/blob/main/pkg/agent/profiler/profiler.go
	// 	ApplicationName: "test222",
	// 	// replace this with the address of pyroscope server
	// 	ServerAddress: "http://localhost:4040",
	// 	// by default all profilers are enabled, but you can select the ones you want to use:
	// 	ProfileTypes: []profiler.ProfileType{
	// 		profiler.ProfileCPU,
	// 		profiler.ProfileAllocObjects,
	// 		profiler.ProfileAllocSpace,
	// 		profiler.ProfileInuseObjects,
	// 		profiler.ProfileInuseSpace,
	// 	},
	// 	DisableGCRuns: true,
	// })
	// run()
}
