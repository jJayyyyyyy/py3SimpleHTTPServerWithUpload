##	Usage:

```bash
$ python3 py3SimpleHTTPServerWithUpload.py
````

然后在浏览器输入 `http://[ip]:8000` 就能上传或者下载文件了。注意把 `[ip]` 换成你的局域网 `ip` 地址。

<br>

##	Workflow

*	确定边界

	假设有文件 `file1.txt`, 其内容如下

	```
	content in file1
	hello file1
	```

	和 `file2.txt`, 其内容如下
	
	```
	content in file2
	hello file2
	```

	如果上传这两个文件, 则在 `HTTP headers` 之后是这样的 `POST data`

	```
	------WebKitFormBoundaryLVlRNkjiiJLtNYQE
	Content-Disposition: form-data; name="file"; filename="file1.txt"
	Content-Type: text/plain

	content in file1
	hello file1
	------WebKitFormBoundaryLVlRNkjiiJLtNYQE
	Content-Disposition: form-data; name="file"; filename="file2.txt"
	Content-Type: text/plain

	content in file2
	hello file2
	------WebKitFormBoundaryLVlRNkjiiJLtNYQE--
	```

	也就是根据这样的 `boundary_start = '------WebKitFormBoundary.....'` 分隔符作为 `POST data` 的边界, 而 `boundary` 可以在 `HTTP headers` 的 `Content-Type` 后面找到

	```python
	def deal_post_data(self):
		print('Content-Type: %s' % self.headers['Content-Type'])
		# Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryAbX7GIRMBXOOJj8p

		boundary = self.headers["Content-Type"].split("=")[1]
		# ----WebKitFormBoundaryAbX7GIRMBXOOJj8p
	```

	读取 `POST data` 的测试代码如下

	```python3
	def deal_post_data(self):
		boundary = self.headers["Content-Type"].split("=")[1]
		remainbytes = int(self.headers['Content-length'])

		line = self.rfile.readline().decode('utf-8')
		print(line)
		remainbytes = remainbytes - len(line)
		if not boundary in line:
			return (False, "Content NOT begin with boundary")

		while remainbytes > 0:
			line = self.rfile.readline().decode('utf-8')
			print(line, end='')
			remainbytes = remainbytes - len(line)
		return(True, '')
	```

*	区块格式

	每一块区域都是这样的格式

	```
	------WebKitFormBoundary...
	filename
	Content-Type

	Content
	```

*	终止条件

	如果是最后一个文件, 那么在其 `Content` 之后会加上一行

	```
	------WebKitFormBoundary...--
	```

	出来了一个小尾巴, 而且后面没有数据了, `remainbytes=0`, 这两个条件都可以作为我们的终止条件, 也就是说

	```
	boundary = '----WebKitFormBoundary...'
	boundary_start = '--' + boundary
	boundary_end = '--' + boundary + '--' 
	```

*	读取数据

	有了以上条件我们就可以从数据流中读取并保存内容了(具体代码请见 `deal_post_data()`)

	<br>

##	Notes:

*	文件夹 `./py2_SimpleHTTPServerWithUpload/` 中存放的是基于 `python2.7` 的模块，在此感谢 [bones7456](http://luy.li/2010/05/15/simplehttpserverwithupload/) 同学和 [BUPTGuo](http://buptguo.com/2015/11/07/simplehttpserver-with-upload-file/) 同学的成果。

*	由于 `python2.7` 和 `Python3.4` 有较多不同特性，原来的程序不能直接在 `python3.4` 的环境中运行，因此我根据以上两位同学的思路，进行了部分重写，制作了基于 `python3.4` 的模块。主要改动如下：

	*	移除了 `StringIO`，不使用 `copyfile()`

		需要传输的信息全都用 `str`, 处理完逻辑后再用 `utf-8` 编码为 `bytes object`，然后放到 `wfile` 上进行传输

	*	修改 `html` 的部分标签顺序

*	根据 @`a.7` 同学的建议, 在上一版本的基础上进行了改进, 使我们可以一次性上传多个文件

*	更多内容请看[这篇博客](https://jjayyyyyyy.github.io/2016/10/07/reWrite_SimpleHTTPServerWithUpload_with_python3.html)

*	原项目地址: https://github.com/jJayyyyyyy/cs/tree/master/just%20for%20fun/file_transfer/http

	现在独立成为一个 `repo`, 方便查找和使用, 也便于维护和升级

*	TODO

	*	步骤：如何安装自己写的模块
	*	单独建立一个 `repo`, 方便查找和使用本模块
	*	更新博客

	<br>

##	Update

*	20181029

	*	根据 @`a.7` 同学的建议, 在上一版本的基础上进行了改进, 使我们可以一次性上传多个文件

		多个文件直接也是用 `boundary` 进行分隔的, 我们正是利用了这点对多个文件进行 `POST`, 我们也可以利用这点区分不同的文件

	*	更新 `deal_post_data()`, 根据 `boundary` 重写逻辑, 以此取代 `remainbytes`

	*	更新 `list_directory()`, 

		根据 [w3schools](https://www.w3schools.com/tags/att_input_multiple.asp), 在 `<input/>` 标签中增加 `multiple="multiple"` 属性, 可以 `accepts multiple values`

	*	增加注释

	*	更新 `readme.md`

	*	修复博文链接

	*	把空格换成了 `tab`, `4 space = 1 tab`
