package sort

func main() {
	quickSort([]int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12})
}

func quickSort(elements []int) {
	if len(elements) < 2 {
		return
	}

	pivot := elements[0]
	i := 1

	for j := 1; j < len(elements); j++ {
		if elements[j] < pivot {
			elements[i], elements[j] = elements[j], elements[i]
			i++
		}
	}
	elements[0], elements[i-1] = elements[i-1], elements[0]

	quickSort(elements[:i-1])
	quickSort(elements[i:])
}

