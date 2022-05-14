package sort

import (
	"fmt"
	"sort"
)

func main() {
	var elements []int
	elements = []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}
	var target = 9

	// sort the array
	i := sort.Search(len(elements), func(i int) bool {
		return elements[i] >= target
	})
	if i < len(elements) && elements[i] == target {
		// found
		fmt.Println("found")
	} else {
		// not found
		fmt.Println("not found")
	}
}