
# selenium
## 查找
在一个页面中有很多不同的策略可以定位一个元素。在你的项目中， 你可以选择最合适的方法去查找元素。Selenium提供了下列的方法给你:

* find_element_by_id                         定位唯一属性id。
* find_element_by_name                  定位带有属性name。
* find_element_by_xpath                  XPath是一种在XML文档中定位元素的语言（比较难*）。
* find_element_by_link_text            定位文本链接。
* find_element_by_partial_link_      textpartial link定位是对 link定位的一种补充，有些文本链接会比较长，这个时候我们可以取文本链接的一部分定位，只要这一部分信息可以唯一地标识这个链接。
* find_element_by_tag_name        如打开任意一个页面，查看前端都会发现大量的<d i v>、<input>, <a>等tag ，所以很难通过标tag name去区分不同的元素。
* find_element_by_class_name    定位带有属性class。
* find_element_by_css_selector   CSS是一种语言，它用来描述HTML和XML文档的表现。CSS使用选择器来为页面元素绑定属性。（比较难*）
1.9 用By定位元素
针对前面介绍的8种定位方法，WebDriver还提供了另外一套写法，即统一调用 find_element()方法  ，通过By来声明定位的方法，并且传入对应定位方法的定位参数。具体如下：

find_element(By.id,"kw")
find_element(By.name,"wd")
find_element(By.class_name,"s_ipt")
find_element(By.tag_name,"input")
find_element(By.link_text,"新 闻 ")
find_element(By.partial_link_text," 新  ")
find_element(By.XPath,"//* [@class = ‘bg s_btn’ ]")
find_element(By.CSS_selector,"span .bg s_btn_wr>input#su")
find_element()方法只用于定位元素。它需要两个参数，第一个参数是定位的类型，由By提供；第二个参数是定位的具体方式。在使用By之前需要将By类导入。
from selenium.webdriver.common.by import By

### 一次查找多个元素 (这些方法会返回一个list列表):

find_elements_by_name
find_elements_by_xpath
find_elements_by_link_text
find_elements_by_partial_link_text
find_elements_by_tag_name
find_elements_by_class_name
find_elements_by_css_selector

### 元素是否可见
>self.driver.find_element_by_id('kw').is_displayed() 返回结果为True或False，True为可见
### 判断元素是否可操作
>self.driver.find_element_by_id('input1').is_enabled() 结果为True或False，True是可操作的

### 判断元素是否已选中
>is_enabled()  判断元素是否可操作
>is_selected()  判断元素是否被选中

## 显示等待
WebDriverWait(driver,timeout,poll_frequency=0.5,ignored_exceptions=None) 
>   driver:浏览器驱动 <br>
    timeout:最长超过时间，默认以秒为单位<br>
    poll_frequency:监测的时间间隔，默认为0.5秒<br>
    ignored_exceptions:超时后的异常信息，默认情况下抛NoSuchElementException异常<br>
    WebDriverWait一般有until和until_not方法配合使用<br>
    until(method,message)<br>
    until_not(method ,message)<br>
————————————————
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
browser.get('https://www.taobao.com/')
wait = WebDriverWait(browser, 10)
input = wait.until(EC.presence_of_element_located((By.ID, 'q'), message="")) # 此处注意，如果省略message=“”，则By.ID外面是两层()
button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-search')))
print(input, button)
```
### EC
1. WebDriverWait(driver,10,0.1).until(EC.title_is("title_text")) 判断title是否是一致,返回布尔值
1. WebDriverWait(driver,10,0.1).until(EC.title_contains("title_text")) 判断title是否与包含预期值,返回布尔值
1. WebDriverWait(driver,10,0.1).until(EC.presence_of_element_located((locator))) 判断某个元素是否被加到了dom树里，并不代表该元素一定可见，如果定位到就返回元素
1. WebDriverWait(driver,10,0.1).until(EC.visibility_of_element_located((locator))) 判断某个元素是否被添加到了dom里并且可见，可见代表元素可显示且宽和高都大于0
1. WebDriverWait(driver,10,0.1).until(EC.visibility_of(driver.find_element(locator))) 判断元素是否可见，如果可见就返回这个元素
1. WebDriverWait(driver,10,0.1).until(EC.presence_of_all_elements_located((locator))) 判断是否至少有1个元素存在于dom树中，如果定位到就返回列表
1. WebDriverWait(driver,10,0.1).until(EC.visibility_of_any_elements_located((locator))) 判断是否至少有一个元素在页面中可见，如果定位到就返回列表
1. WebDriverWait(driver,10,0.1).until(EC.text_to_be_present_in_element((locator),'预期的text')) 判断指定的元素中是否包含了预期的字符串，返回布尔值
1. WebDriverWait(driver,10,0.1).until(EC.text_to_be_present_in_element_value((locator),'预期的text')) 判断指定元素的value属性值中是否包含了预期的字符串，返回布尔值(注意：只是value属性)
1. WebDriverWait(driver,10,0.1).until(EC.frame_to_be_available_and_switch_to_it(locator)) 判断该frame是否可以switch进去，如果可以的话，返回True并且switch进去，否则返回False
1. WebDriverWait(driver,10,0.1).until(EC.invisibility_of_element_located((locator))) 判断某个元素在是否存在于dom或不可见,如果可见返回False,不可见返回这个元素
1. WebDriverWait(driver,10,0.1).until(EC.element_to_be_clickable((locator))) 判断某个元素是否可见并且是可点击的，如果是的就返回这个元素，否则返回
1. WebDriverWait(driver,10,0.1).until(EC.staleness_of(driver.find_element(locator))) 等待某个元素从dom树中移除
1. WebDriverWait(driver,10,0.1).until(EC.element_to_be_selected(driver.find_element(locator))) 判断某个元素是否被选中了,一般用在下拉列表
1. WebDriverWait(driver,10,0.1).until(EC.element_selection_state_to_be(driver.find_element(locator),True)) 判断某个元素的选中状态是否符合预期
1. WebDriverWait(driver,10,0.1).until(EC.element_located_selection_state_to_be((locator),True)) 判断某个元素的选中状态是否符合预期
1. accept = WebDriverWait(driver,10,0.1).until(EC.alert_is_present()) 判断页面上是否存在alert,如果有就切换到alert并返回alert的内容

### BY
1. (By.ID, 'username')
1. (By.TAG_NAME, 'button')
1. (By.XPATH, "//span[text()='新建投放计划']")

## 隐式等待

>当查找元素或元素并没有立即出现的时候，隐式等待将等待一段时间再查找 DOM，默认的时间是0

```python
from selenium import webdriver

browser = webdriver.Chrome()
browser.implicitly_wait(10) #等待十秒加载不出来就会抛出异常，10秒内加载出来正常返回
browser.get('https://www.zhihu.com/explore')
input = browser.find_element_by_class_name('zu-top-add-question')
print(input)
```

# 问题？
1. 判断满足多个条件

1. 动态出现 alert


#
解析库
1.beautifulSoup
2. PyQuery   实现jquery
3.xPath

解决js渲染问题
1. 分析ajax
2.webdriver 一个自动化测试工具，模拟浏览器请求
3.splash 模拟浏览器库
4.PyV8、Ghost.py

查看关系数据库工具dataGrip
robomongo

python 库
1. urllib  py内置http请求库
2. requests
http://httpbin.org/  可用于http请求验证
代理（这个可以重看 27m左右）

正则 tool.oschina.net/regex

selenium 模拟加载 js 渲染问题


mysql
python基础
多线程
urllib.parse  urlencode(data)  把字段转成get 参数
json.load()

链接mongodb 【抓头条】27m


python 全局安装
1. flask 比较轻量的
2. scrapy 重点
3.pySpider

爬虫框架


scrapy 安装（https://www.jianshu.com/p/14950bfd271b）


命令
scrapy startproject 项目名
cd 项目名
scrapy genspider quotes quotes.toscrape.com
scrapy crawl quotes

scrapy crawl  -a user=user name=name  // 传参数 __init__ 获取

scrapy crawl quotes -o quotes.json
scrapy crawl quotes -o quotes.jl // jion 没有前后的中括号
scrapy crawl quotes -o quotes.csv
scrapy crawl quotes -o quotes.xml   // .pickle  .marshal 
scrapy fetch --nolog www.baidu.com // 请求
scrapy view www.baidu.com // 跳出浏览器打开
scrapy shell quotes.toscrape.com // 命令行交互调试  如输入：response 和 response.css('.quotes')
scrapy parse <url>
scrapy settings -- get
scrapy runspider  <file.py> // 运行一个文件
scrapy bench // 测试爬行速度

Anaconda 装scrapy
conda list  列表安装的库
conda install scrapy 

middlewares 处理代理

result = json.loads(response.text)
result.get('key')

# 生成依赖文件 - 安装依赖
pip3 freeze > requirements.txt
pip3 install -r requirements.txt
