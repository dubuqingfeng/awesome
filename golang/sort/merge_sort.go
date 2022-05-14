package sort

func main() {
	// by copilot
	MergeSort([]int{})
}

func MergeSort(elements []int) {
	if len(elements) <= 1 {
		return
	}

	middle := len(elements) / 2
	left := elements[:middle]
	right := elements[middle:]

	MergeSort(left)
	MergeSort(right)

	merge(left, right, elements)
}

func merge(left []int, right []int, elements []int) {
	i := 0
	j := 0
	k := 0

	for i < len(left) && j < len(right) {
		if left[i] < right[j] {
			elements[k] = left[i]
			i++
		} else {
			elements[k] = right[j]
			j++
		}
		k++
	}

	for i < len(left) {
		elements[k] = left[i]
		i++
		k++
	}

	for j < len(right) {
		elements[k] = right[j]
		j++
		k++
	}
}