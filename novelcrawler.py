#!/usr/bin/env python
#coding:utf-8

import re
import json
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

chs_arabic_map = {u'零':0, u'一':1, u'二':2,'两':2, u'三':3, u'四':4,
        u'五':5, u'六':6, u'七':7, u'八':8, u'九':9,
        u'十':10, u'百':100, u'千':10 ** 3, u'万':10 ** 4,
        u'〇':0, u'壹':1, u'贰':2, u'叁':3, u'肆':4,
        u'伍':5, u'陆':6, u'柒':7, u'捌':8, u'玖':9,
        u'拾':10, u'佰':100, u'仟':10 ** 3, u'萬':10 ** 4,
        u'亿':10 ** 8, u'億':10 ** 8, u'幺': 1,
        u'０':0, u'１':1, u'２':2, u'３':3, u'４':4,
        u'５':5, u'６':6, u'７':7, u'８':8, u'９':9}

class mail(object):
	def __init__(self):
		self.sender='opmyqp@163.com'
		self.host='smtp.163.com'
		self.rec=['1832138943@qq.com']
		self.usr='opmyqp'
		self.pwd='renxiaoyao12036'

	def construct(self):
		self.msg=MIMEMultipart()
		self.msg['From']=self.sender
		self.msg['To']=self.rec[0]
		self.msg['Subject']='update'
		content=MIMEText(open('updateRecorder.html', 'r').read(), _subtype='html', _charset='utf-8')

		self.msg.attach(content)
		try:
			self.smtplibObj=smtplib.SMTP()
			self.smtplibObj.connect(self.host, 25)
			self.smtplibObj.login(self.usr, self.pwd)
			self.smtplibObj.sendmail(self.sender, self.rec, self.msg.as_string())
			self.smtplibObj.quit()
			print('send successfully!')
		except smtplib.SMTPException as e:
			raise e

class crawler(object):
	def __init__(self):
		self.header={'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT'}
		self.mail=mail()
	
	def convert(self, chinese_digits, encoding="utf-8"):
		result=0
		tmp=0
		hnd_mln=0
		for count in range(len(chinese_digits)):
			curr_char=chinese_digits[count]
			curr_digit=chs_arabic_map.get(curr_char, None)
			# meet 「亿」 or 「億」
			if curr_digit==10 ** 8:
				result=result + tmp
				result=result * curr_digit
				# get result before 「亿」 and store it into hnd_mln
				# reset `result`
				hnd_mln=hnd_mln * 10 ** 8 + result
				result=0
				tmp=0
			# meet 「万」 or 「萬」
			elif curr_digit == 10 ** 4:
				result=result + tmp
				result=result * curr_digit
				tmp= 0
			# meet 「十」, 「百」, 「千」 or their traditional version
			elif curr_digit >= 10:
				tmp = 1 if tmp == 0 else tmp
				result=result+curr_digit*tmp
				tmp=0
			# meet single digit
			elif curr_digit is not None:
				tmp = tmp * 10 + curr_digit
			else:
				return result
		result = result + tmp
		result = result + hnd_mln
		return result

	def getNum(self, chapterName):
		resList=chapterName.split()
		if len(resList)==3:
			pattern=re.compile(r'\d+')
			return int((pattern.findall(resList[1]))[0])
		elif len(resList)==2:
			a=resList[1].split('章')
			b=a[0].split('第')
			return self.convert(b[1])

	def store(self, novelName, num, chapterName):
		with open('updateRecorder.html', 'a+') as f:
			f.write('<tr><td>%s</td><td>%s</td><td>%s</td></tr>'%(novelName, num, chapterName))
			f.close()


	def isUpdate(self, novelName, latestChapter):
		searchUrl='https://www.qidian.com/search?kw='+novelName
		req=requests.get(searchUrl, headers=self.header)
		if req.status_code==200:
			soup=BeautifulSoup(req.text, 'html.parser', from_encoding='utf-8')
			chapterName=soup.find('p', class_='update').find('a').string
			num=self.getNum(chapterName)
			# resList=chapterName.split()
			# pattern=re.compile(r'\d+')
			# num=int((pattern.findall(resList[1]))[0])
			if num>latestChapter:
				return True, num, chapterName
			else:
				return False, latestChapter, None
		else:
			logging.warning("vertify failed: the status_code is %d"%req.status_code)
	

	def craw(self, novelName, latestChapter):
		bUpdate, num, chapterName=self.isUpdate(novelName, latestChapter)
		# if bUpdate:
		# 	searchUrl='https://www.baidu.com/s?wd='+novelName
		# 	req=requests.get(searchUrl, headers=self.header)
		# 	result=
		# 	i=0
		# 	if req.status_code==200:
		# 		soup=BeautifulSoup(req.text, 'html.parser')
		# 		cgrays=soup.find_all('p', class_='c-gray')
		# 		pattern=re.compile(r'[\d+,]')
		# 		for cgray in cgrays:
		# 			i+=1
		# 			tag=cgray.find('a')
		# 			L['title']=tag.string
		# 			if i>1:

		# 			L['href']=tag.get('href')
		if bUpdate==True:
			self.store(novelName, num, chapterName)
			with open('novellist.json', 'r') as jf:
				f=json.load(jf)
				jf.close()
			for i in range(len(f['content'])):
				name=f['content'][i]['name']
				if name==novelName:
					f['content'][i]['latestChapter']=num
					break
			with open('novellist.json', 'w') as jf:
				json.dump(f,jf)
				jf.close()
			
if __name__ == '__main__':
	c=crawler()
	with open('updateRecorder.html', 'w') as f:
		f.write("<html><body><table border='1'>")
		f.close()

	with open('novellist.json', 'r') as jf:
		f=json.load(jf)
		for i in range(len(f['content'])):
			novelName=f['content'][i]['name']
			latestChapter=f['content'][i]['latestChapter']
			c.craw(novelName,latestChapter)
		jf.close()
	with open('updateRecorder.html', 'a+') as f:
		f.write('</table></body></html>')
		f.close()
	c.mail.construct()
