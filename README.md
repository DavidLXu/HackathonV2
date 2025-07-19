我们设计了一款智慧冰箱，是圆柱形的结构，中间有一个圆形平台可以上升下降以及旋转取物，四周是储物的扇区，每一层大概有2-6个扇区，一共4-6层，冰箱层的温度自底向上逐渐升高，由此实现不同的温度分区，以及同层之间的扇区隔离。
思想比较类似智慧仓储。

我们想要一个智能化的冰箱Agent，主要功能构思如下

用户在使用冰箱时，圆形平台上升到圆筒的顶部，这是冰箱的入口。用户只需要关注把食材往平台上放，平台自动的去接管食材应该放到哪里。当用户取物时，圆形平台的机械结构会去对应的位置把食材取出来。从用户的角度，他只管放和取，不管具体的存放方式。

Agent 功能点1
中间的圆形平台具有三个自由度：上下移动定位到各层（整数），旋转朝向各个扇区（整数），以及一个开关量来让圆形平台上的机械臂去扇区内取物（布尔值）。这三个功能分别对应三个函数，用function calling去调用
我的智慧冰箱底层已经实现好了这三个函数用于冰箱的控制
def lift(level_index):
    print(f"reached level {level_index}")
def turn(section_index):
    print(f"turned to section {section_index}")
def fetch():
    print("fetched object")

Agent 功能点2
新物品放入时，会从相机读取一个图像，如some_food.jpg，调用Qwen VL判断大致的物体种类，通过Qwen VL获取这种物体对应的保质期，通过Qwen VL获取这种物体对应的最佳存放温度，和已有冰箱的温度分层做好配合。放置到合适的层高和没有被使用的扇区。Agent应该维护一个json文件来记录不同层高扇区内存放的物品，根据记录的放入时间和物品种类，可以实时计算保质期还有多长。

Agent 功能点3
根据用户的偏好和食材的保存时间，主动给出用户推荐，如果用户同意，冰箱就直接找到对应的地方把食材取出来。这种proactive的模式，可以防止用户不知道自己想要什么。

充分使用Qwen VL模型的function calling能力，不要写rule-based来控制冰箱，也不需要提前保存任何关于不同食物的种类与保存天数，只需要维护一个json来记录冰箱已经有的东西，剩下的逻辑与对新食物的判断全交给大模型,帮我写好与大模型交互的prompt来最好的实现我的要求。食物种类做到open vocabulary

所有的逻辑全都用大模型调用来实现，包括食材推荐，把目前冰箱物品的状态和用户偏好上传，让大模型进行推理，不要在本地写规则。

## Setup

### Environment Variables

1. Set your DashScope API key as an environment variable:
   ```bash
   export DASHSCOPE_API_KEY="your_api_key_here"
   ```
   
   Or create a `.env` file in the project root:
   ```
   DASHSCOPE_API_KEY=your_api_key_here
   ```

2. Get your API key from: https://dashscope.console.aliyun.com/

### Installation

1. Install required packages:
   ```bash
   pip install dashscope flask
   ```

2. Run the application:
   ```bash
   python web_interface.py
   ```