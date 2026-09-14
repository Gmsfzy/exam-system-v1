import pandas as pd

# 完整题库数据
data = """题型	题干	选项A	选项B	选项C	选项D	答案	分数
single	下列哪个不是Python的合法标识符？	_abc	abc123	123abc	Abc123	C	2
single	Python中表示注释的符号是？	//	#	/* */	--	B	2
single	下列哪个数据类型是Python的基本数据类型？	list	dict	int	set	C	2
single	Python中，字符串的定义使用？	单引号	双引号	三引号	以上都是	D	2
single	以下哪个运算符是整除？	/	//	%	**	B	2
single	Python中，判断相等使用？	=	==	===	!=	B	2
single	下列哪个语句用于循环遍历序列？	if	for	while	break	B	2
single	Python中定义函数使用的关键字是？	def	func	function	define	A	2
single	以下哪个是Python的列表？	()	[]	{}	<>	B	2
single	列表中添加元素的方法是？	add	insert	append	push	C	2
single	Python字典使用什么符号定义？	[]	()	{}	<>	C	2
single	下列哪个是Python的文件打开模式（只读）？	r	w	a	x	A	2
single	Python中导入模块使用？	include	require	import	from	C	2
single	下列哪个不是Python的循环结构？	for	while	do-while	以上都不是	C	2
single	Python中，break语句的作用是？	结束本次循环	跳出整个循环	跳过条件	程序终止	B	2
single	下列哪个是Python的异常处理关键字？	catch	try	throw	exception	B	2
single	Python中，创建类使用关键字？	class	struct	type	object	A	2
single	面向对象中，封装的目的是？	提高速度	保护数据	简化代码	减少内存	B	2
single	下列哪个方法是Python的构造方法？	__init__	__str__	__del__	__main__	A	2
single	Python中，self代表？	类本身	对象本身	父类	模块	B	2
single	下列哪个不是Python的访问权限修饰符？	public	private	protected	没有	D	2
single	Python中，读取键盘输入使用？	input	read	get	scan	A	2
single	下列哪个函数可以获取字符串长度？	len	size	count	length	A	2
single	Python中，range(5)生成的序列是？	0-4	1-5	0-5	1-4	A	2
single	下列哪个是Python的元组？	[]	{}	()	<>	C	2
single	元组和列表的区别是？	元组可修改	列表不可修改	元组不可修改	没有区别	C	2
single	Python中，集合的特点是？	有序可重复	无序不重复	有序不重复	无序可重复	B	2
single	下列哪个是Python的布尔值？	true	True	yes	no	B	2
single	Python中，逻辑与运算符是？	&	&&	and	OR	C	2
single	下列哪个函数可以将字符串转为整数？	float	str	int	bool	C	2
single	Python文件扩展名是？	.py	.java	.c	.js	A	2
single	下列哪个不是Python的Web框架？	Django	Flask	Spring	FastAPI	C	2
single	Python中，pass语句作用？	抛出异常	空语句，不执行	结束程序	重启循环	B	2
single	下列哪个方法可以删除列表元素？	remove	delete	drop	clear	A	2
single	Python中，字符串切片 s[1:3] 表示？	第1到第3个	第1到第2个	第0到第3个	第2到第3个	B	2
single	下列哪个是Python的深拷贝？	copy	deepcopy	clone	assign	B	2
single	Python中，全局变量关键字？	global	public	private	extern	A	2
single	下列哪个不是Python的数据结构？	list	tuple	map	dict	C	2
single	Python中，打开文件并写入使用？	r	w	a	rb	B	2
single	下列哪个是Python的迭代器？	for循环	range()	生成器	以上都是	D	2
single	Python中，lambda表达式用于？	定义类	定义匿名函数	异常处理	模块导入	B	2
single	下列哪个方法可以对列表排序？	sort	order	arrange	filter	A	2
single	Python中，判断变量类型使用？	type	isinstance	check	typeof	A	2
single	下列哪个不是Python的异常？	IndexError	NameError	SyntaxError	NullError	D	2
single	Python中，super()作用？	调用父类	调用子类	调用自身	调用模块	A	2
single	下列哪个是Python的装饰器符号？	@	&	$	#	A	2
single	Python中，多继承表示？	一个类继承多个类	多个类继承一个类	类继承自身	不支持多继承	A	2
single	下列哪个函数可以返回最大值？	max	min	sum	avg	A	2
single	Python中，列表推导式的格式是？	[表达式 for 变量 in 列表]	{表达式 for 变量 in 列表}	(表达式 for 变量 in 列表)	<表达式 for 变量 in 列表>	A	2
single	下列哪个不是Python的内置函数？	print	input	open	printf	D	2
single	Python中，continue语句作用？	跳出循环	结束本次循环，进入下一次	终止程序	跳过函数	B	2
single	下列哪个是Python的随机数模块？	math	random	time	os	B	2
single	Python中，os模块用于？	网络请求	文件/目录操作	数学计算	时间处理	B	2
single	下列哪个方法可以将列表转为字符串？	join	split	strip	replace	A	2
single	Python中，strip()作用？	分割字符串	去除首尾空格	替换字符	转大写	B	2
single	下列哪个是Python的格式化输出？	%s	%d	f-string	以上都是	D	2
single	Python中，字典获取值使用？	[]	()	.	{}	A	2
single	下列哪个不是Python的关键字？	if	else	main	while	C	2
single	Python中，创建虚拟环境使用？	venv	virtualenv	pip	conda	A	2
single	下列哪个是Python的科学计算库？	numpy	pandas	matplotlib	以上都是	D	2
single	Python中，判断字符串是否包含子串使用？	in	contains	exist	include	A	2
multiple	Python的基本数据类型包括？	int	float	str	list	ABC	3
multiple	下列哪些是Python的循环结构？	for	while	do-while	foreach	AB	3
multiple	Python中序列类型包括？	list	tuple	str	dict	ABC	3
multiple	下列哪些是Python的映射类型？	list	dict	set	None	B	3
multiple	Python函数的参数类型包括？	位置参数	关键字参数	默认参数	可变参数	ABCD	3
multiple	下列哪些是Python的文件打开模式？	r	w	a	t	ABC	3
multiple	Python面向对象三大特性？	封装	继承	多态	重载	ABC	3
multiple	下列哪些是Python的异常处理关键字？	try	catch	except	finally	ACD	3
multiple	Python中字符串常用方法？	strip()	split()	join()	append()	ABC	3
multiple	下列哪些是Python的内置函数？	print	len	input	def	ABC	3
multiple	Python列表常用方法？	append()	remove()	insert()	sort()	ABCD	3
multiple	下列哪些可以表示Python注释？	#	//	""" """	/* */	AC	3
multiple	Python逻辑运算符包括？	and	or	not	&&	ABC	3
multiple	下列哪些是Python的模块？	os	time	random	math	ABCD	3
multiple	Python字典常用操作？	增加键值对	删除键值对	修改值	遍历	ABCD	3
multiple	下列哪些是Python的合法变量名？	name1	_name	1name	name_123	ABD	3
multiple	Python中可以实现循环的语句？	for	while	if	break	AB	3
multiple	下列哪些属于Python数据结构？	list	tuple	dict	set	ABCD	3
multiple	Python函数返回值使用？	return	yield	exit	break	AB	3
multiple	下列哪些是Python的标准库？	flask	os	sys	time	BCD	3
judge	Python是编译型语言	False	2
judge	Python对大小写敏感	True	2
judge	列表是不可变类型	False	2
judge	元组是不可变类型	True	2
judge	break可以跳出所有循环	False	2
judge	continue会终止整个循环	False	2
judge	Python使用缩进来表示代码块	True	2
judge	lambda可以定义有名称的函数	False	2
judge	字典的键可以重复	False	2
judge	集合中的元素不允许重复	True	2
judge	Python不支持面向对象编程	False	2
judge	__init__是类的构造方法	True	2
judge	self必须作为方法的第一个参数	True	2
judge	Python支持多继承	True	2
judge	pass语句什么都不执行	True	2
judge	except可以捕获所有异常	True	2
judge	文件打开后必须关闭	True	2
judge	import可以导入自定义模块	True	2
judge	range(1,5)生成1,2,3,4	True	2
judge	Python中=表示判断相等	False	2
"""

# 解析数据并生成Excel
lines = [line.split('\t') for line in data.strip().split('\n')]
df = pd.DataFrame(lines[1:], columns=lines[0])
df.to_excel('python_exam_100.xlsx', index=False)
print("✅ 生成成功！文件：python_exam_100.xlsx")