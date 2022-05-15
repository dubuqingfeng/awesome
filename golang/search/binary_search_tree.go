package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func main() {
	// binary search tree
	var root *TreeNode
	root = &TreeNode{
		Val: 1,
		Left: &TreeNode{
			Val: 2,
			Left: &TreeNode{
				Val: 3,
				Left: &TreeNode{
					Val:  4,
					Left: &TreeNode{},
				},
			},
		},
		Right: &TreeNode{
			Val: 5,
			Left: &TreeNode{
				Val: 6,
				Left: &TreeNode{
					Val:  7,
					Left: &TreeNode{},
				},
				Right: &TreeNode{
					Val:  8,
					Left: &TreeNode{},
				},
			},
			Right: &TreeNode{
				Val:  9,
				Left: &TreeNode{},
			},
		},
	}
}
