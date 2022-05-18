package filewatcher

import (
	"fmt"
	"io/fs"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

const (
	defaultTickRate int64 = 5
)

type FileFn func(de DirEntry) error

var DefaultFileFn = func(de DirEntry) error {
	fmt.Printf("entry has been updated recently:\n\tpath=%q\n\tname=%q\n\tsize=%d\n\n", de.Path, de.Name, de.Size)
	return nil
}

type FileWatcher struct {
	basePath   string
	regexMatch *regexp.Regexp
	fileFn     FileFn
	tickRate   int64
	ticker     *time.Ticker
	stop       chan struct{}
	isRunning  bool
}

func NewFileWatcher(basePath, regexMatch string, fileFn FileFn) *FileWatcher {
	return &FileWatcher{
		basePath:   basePath,
		regexMatch: regexp.MustCompile(regexMatch),
		fileFn:     fileFn,
		tickRate:   defaultTickRate,
		ticker:     time.NewTicker(time.Duration(defaultTickRate) * time.Second),
		stop:       make(chan struct{}),
	}
}

func (fw *FileWatcher) IsRunning() bool {
	return fw.isRunning
}

func (fw *FileWatcher) Stop() {
	if !fw.IsRunning() {
		// if it is already stopped, do not stop again
		return
	}
	fw.ticker.Stop()
	fw.stop <- struct{}{}
}

func (fw *FileWatcher) Start() {
	if fw.IsRunning() {
		// if it is already running, do not run again
		return
	}
	log.Printf("FileWatcher is running. (polling every %d seconds)\n", fw.tickRate)
	fw.isRunning = true
	go func() {
		for {
			select {
			case <-fw.ticker.C:
				// when the ticker fires, run the file watcher
				// and push any changes onto the files channel
				fw.checkOnFiles()
			case <-fw.stop:
				// if we get a stop signal, stop ticking
				log.Println("FileWatcher is stopped.")
				fw.isRunning = false
				return
			}
		}
	}()
}

func (fw *FileWatcher) checkOnFiles() {
	// walk path and see if we can find any files that match our matcher and
	// may be ready to be updated
	err := filepath.WalkDir(
		fw.basePath, func(path string, de fs.DirEntry, err error) error {
			if err != nil {
				fmt.Fprintf(os.Stderr, "prevent panic by handling failure accessing a path %q: %v\n", path, err)
				return err
			}
			// skip hidden files and directories
			if strings.HasPrefix(de.Name(), ".") {
				return fs.SkipDir
			}
			// see if this dir entry returns a found match against our matcher
			if gotMatch := fw.regexMatch.MatchString(de.Name()); gotMatch {
				// we have found a match, so lets check to see if this particular
				// dir entry has been updated in the last tickRate seconds...
				if getEntryModTime(de).Unix() >= (time.Now().Unix() - fw.tickRate) {
					// this dir entry has been updated recently, so run supplied file func
					err = fw.fileFn(
						DirEntry{
							Name:    de.Name(),
							Path:    filepath.ToSlash(path),
							Size:    getEntrySize(de),
							ModTime: getEntryModTime(de),
						},
					)
					if err != nil {
						return err
					}
				}
			}
			// otherwise, we should just return
			return nil
		},
	)
	// check for errors
	if err != nil {
		fmt.Fprintf(os.Stderr, "%s", err)
	}
}

func getEntryInfo(de fs.DirEntry) (int64, time.Time) {
	dei, err := de.Info()
	if err != nil {
		fmt.Fprintf(os.Stderr, "%s", err)
	}
	return dei.Size(), dei.ModTime()
}

func getEntrySize(de fs.DirEntry) int64 {
	sz, _ := getEntryInfo(de)
	return sz
}

func getEntryModTime(de fs.DirEntry) time.Time {
	_, mt := getEntryInfo(de)
	return mt
}

type DirEntry struct {
	Name    string
	Path    string
	Size    int64
	ModTime time.Time
}
