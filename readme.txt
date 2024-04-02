ในการทำงานของโปรแกรมที่ผู้เรียนได้ทำการพัฒนาเอาไว้เพื่อ implement service ของ ftp client ด้วย socket programming โดยใช้ tcp protocol (SOCK_STREAM) โดยได้สร้างให้มีการทำงานได้ดังนี้ (ทั้งหมดนั่นเอง)
•ascii(2 คะแนน)
•binary(2 คะแนน)
•bye(1 คะแนน)
•cd(2 คะแนน)
•close(1 คะแนน)
•delete(2 คะแนน)
•disconnect(1 คะแนน)
•get(2 คะแนน)
•ls(2 คะแนน)
•open(2 คะแนน)
•put(2 คะแนน)
•pwd(2 คะแนน)
•quit(1 คะแนน)
•rename(2 คะแนน)
•user(2 คะแนน)
และโครงสร้างหลักของโปรแกรมสามารถทำงานแบบ Read-Evaluate-Print-Loop (REPL) และรับคำสั่งได้
มีการใช้ time ในการคำนวณหา transfer rate ทำให้อาจไม่ตรงกับ ftp ต้นฉบับ
มีการใช้ getpass library ในส่วนการกรอกรหัส user เพื่อให้เหมือนกับต้นฉบับ
มีการใช้ os เพื่อ get current directory ใน put fuction