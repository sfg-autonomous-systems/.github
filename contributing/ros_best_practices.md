# ROS Best Practices

## Publish/Subscribe Signatures

When publishing messages in a ROS node, you should **(whenever possible) supply a `std::unique_ptr<MsgType>` to the `publish(...)` function**. This ensures that the publisher can leverage intra-process communication as detailed [here](https://docs.ros.org/en/humble/Tutorials/Demos/Intra-Process-Communication.html).

For the same reason, your callback signature should **(whenever possible) use `const MsgType::ConstSharedPtr &msg` to subscribe to a topic**. In case of subscriptions a case for using `std::unique_ptr<MsgType>` can be made but this is only better if you are certain only a single subscriber will subscribe to a given topic. Therefore, as a best-fit compromise, stick to `const MsgType::ConstSharedPtr &msg`!