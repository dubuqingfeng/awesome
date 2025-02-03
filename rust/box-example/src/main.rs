fn main() {
    // 基本使用：在堆上分配一个整数
    let boxed_int = Box::new(42);
    println!("Boxed integer: {}", *boxed_int); // 使用 * 解引用

    // 所有权转移
    let new_owner = boxed_int; // boxed_int 的所有权转移
    // println!("{}", boxed_int); // 这里会编译错误，因为所有权已经转移
    println!("New owner: {}", new_owner);

    // 使用 Box 创建递归类型（链表节点示例）
    #[derive(Debug)]
    enum ListNode {
        Node(i32, Box<ListNode>),
        End,
    }

    // 创建链表 1 -> 2 -> 3 -> End
    let list = ListNode::Node(
        1,
        Box::new(ListNode::Node(
            2,
            Box::new(ListNode::Node(3, Box::new(ListNode::End))),
        )),
    );

    println!("Linked list: {:?}", list);

    // 手动释放内存（通常不需要，演示 Drop trait 的工作）
    let will_be_dropped = Box::new(String::from("Hello Box!"));
    println!("Before drop: {}", will_be_dropped);
    // drop(will_be_dropped); // 手动释放（取消注释会导致最后一行编译错误）
    println!("After drop: {}", will_be_dropped); // 自动释放，仍然可以访问
}