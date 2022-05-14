package main

func main() {
	const numWorkers = 10
	jobs := make(chan int, numWorkers)
	results := make(chan int, numWorkers)

	for i := 0; i < numWorkers; i++ {
		go worker(i, jobs, results)
	}

	for j := 0; j < numWorkers; j++ {
		jobs <- j
	}
	close(jobs)

	for a := 0; a < numWorkers; a++ {
		<-results
	}
}

func worker(i int, jobs chan int, results chan int) {
	for j := range jobs {
		results <- j * 2
	}
}
