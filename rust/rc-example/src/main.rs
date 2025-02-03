use std::rc::Rc;

fn main() {
    // 创建一个 Rc 实例，包含一个整数
    let rc_value = Rc::new(42);

    // 克隆 Rc，增加引用计数
    let rc_clone1 = Rc::clone(&rc_value);
    let rc_clone2 = Rc::clone(&rc_value);

    // 打印引用计数
    println!("Reference count after cloning: {}", Rc::strong_count(&rc_value));

    // 使用 Rc 的值
    println!("rc_value: {}", rc_value);
    println!("rc_clone1: {}", rc_clone1);
    println!("rc_clone2: {}", rc_clone2);

    // 当 rc_clone1 和 rc_clone2 离开作用域时，引用计数会减少
    // 当 rc_value 离开作用域时，引用计数会变为零，内存会被释放
}
