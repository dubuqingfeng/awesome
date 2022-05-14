package main

import "fmt"

// https://stackoverflow.com/questions/55273965/how-to-know-if-goroutine-still-exist
// number of desired workers
const nWorkers = 10

func main() {
        // make a buffered channel with the space for my 10 workers
        workerChan := make(chan *worker, nWorkers)
        for i := 0; i < nWorkers; i++ {
                i := i
                wk := &worker{id: i}
                go wk.work(workerChan)
        }
        // read the channel, it will block until something is written, then a new
        // goroutine will start
        for wk := range workerChan {
                // log the error
                fmt.Printf("Worker %d stopped with err: %s", wk.id, wk.err)
                // reset err
                wk.err = nil
                // a goroutine has ended, restart it
                go wk.work(workerChan)
        }
}

type worker struct {
        id  int
        err error
}

func (wk *worker) work(workerChan chan<- *worker) (err error) {
        defer func() {
                if r := recover(); r != nil {
                        if err, ok := r.(error); ok {
                                wk.err = err
                        } else {
                                wk.err = fmt.Errorf("Panic happened with %v", r)
                        }
                } else {
                        wk.err = err
                }
                workerChan <- wk
        }()
        return err
}