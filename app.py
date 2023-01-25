import sqlite3 as sql
from os import path
from flask import Flask, request, jsonify
app = Flask(__name__)

dbname = "students_marks.db"
if not path.isfile(dbname):
    connect = sql.connect(dbname)
    cur = connect.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS students_marks (

                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    first_name TEXT,
                                    last_name TEXT,
                                    subject TEXT,
                                    point FLOAT DEFAULT 0
                                      )""")
    connect.close()
    print("Database successfully created")
else:
    print("Database allready exists")


class options:
    def __init__(self,dbfile):
        self.connection = sql.connect(dbfile)
    def escape(self,d_string):
        d_string = d_string.replace("'","`")
        return d_string.strip()

    def load_data(self,id):
        if id != None:
            cur = self.connection.cursor()
            cur.execute(f"SELECT * from students_marks where id={id}")
            data = cur.fetchone()

            self.connection.close()
            return data
        else:
            cur = self.connection.cursor()
            cur.execute(f"SELECT * from students_marks order by id desc")
            data = cur.fetchall()
            self.connection.close()
            return data

    def add_new(self,first_name,last_name,subject,point):
        cur = self.connection.cursor()
        add = cur.execute(f"INSERT INTO students_marks (first_name,last_name,subject,point) VALUES ('{self.escape(first_name)}','{self.escape(last_name)}','{self.escape(subject)}','{point}')")
        self.connection.commit()
        self.connection.close()
        return "successfully added"
    def delete(self,id):
        cur = self.connection.cursor()
        delete = cur.execute(f"DELETE FROM students_marks WHERE id={id}")
        self.connection.commit()
        self.connection.close()
        if delete.rowcount == 1:
            return f"successfully deleted"
        else:
            return f"There is no any record where id = {id}"

    def update(self,info,update_by):
        cur = self.connection.cursor()

        if update_by != "insert":
            update = {}
            for key,value in info.items():
                if key == "id" or update_by == key:
                    continue
                if value != None:
                    if len(value) == 0:
                        return f"{key} must be filled"
                    update[key]=value
            if len(update) == 0:
                return "You must specify at least one update parameter"
            else:
                if info['point'] != None:
                    try:
                        point = float(info['point'])
                    except ValueError:
                        return "Point must be float"
                    except:
                        return "Something went wrong"
                up = ','.join([key+"='"+str(self.escape(value))+"'" for key,value in update.items()])
                #print(f"UPDATE students_marks SET {up} WHERE {update_by}='{self.escape(str(info[update_by]))}'")
                update = cur.execute(f"UPDATE students_marks SET {up} WHERE {update_by}='{self.escape(str(info[update_by]))}'")

                self.connection.commit()
                self.connection.close()
                if update.rowcount > 0:
                    return "successfully updated"
                else:
                    return f"There is no any record where {update_by} = {self.escape(str(info[update_by]))}"
        else:
            res = self.add_new(info['first_name'],info['last_name'],info['subject'],info['point'])
            return res





@app.route("/<int:id>", methods=['GET'])
def load_data(id):
    for_load = options(dbname)
    resp = for_load.load_data(id)
    if resp == None:
        return "There is no any record in database"
    else:
        result = {}
        result[0] = {"id":resp[0],"first_name":resp[1],"last_name":resp[2],"subject":resp[3],"point":resp[4]}
        return jsonify(result)
@app.route("/", methods=['GET'])
def load_full():
    for_load = options(dbname)
    resp = for_load.load_data(None)
    if resp == None:
        return "There is no any record in database"
    else:
        result = {}
        i=0
        for each in resp:
            result[i] = {"id":each[0],"first_name":each[1],"last_name":each[2],"subject":each[3],"point":each[4]}
            i+=1
        return jsonify(result)

@app.route("/add", methods=['POST'])
def add_row():
    first_name = request.args.get("first_name", None, type=str)
    last_name = request.args.get("last_name", None, type=str)
    subject = request.args.get("subject", None, type=str)
    point = request.args.get("point", None)
    if first_name == None or last_name == None or subject == None or point == None:
        return f"All fields must be filled"
    elif len(first_name.strip())==0:
        return f"First name must be filled"
    elif len(last_name.strip())==0:
        return f"Last name must be filled"
    elif len(subject.strip())==0:
        return f"Subject must be filled"
    elif len(str(point).strip())==0:
        return f"Point must be filled"
    else:
        try:
            point = float(point)
        except ValueError:
            return "Point must be float"
        except:
            return "Something went wrong"
        for_add = options(dbname)
        added = for_add.add_new(first_name,last_name,subject,point)
        return f"{added}"
@app.route("/delete", methods=['DELETE'])
def delete():
    for_delete = options(dbname)
    id = request.args.get("id", None)
    if id == None:
        return "Add id parameter"
    try:
        id = int(id)
    except ValueError:
        return "id must be integer"
    except:
        return "Something went wrong"
    resp = for_delete.delete(id)
    return resp


@app.route("/update", methods=['PUT'])
def update():
    for_delete = options(dbname)

    first_name = request.args.get("first_name", None, type=str)
    last_name = request.args.get("last_name", None, type=str)
    subject = request.args.get("subject", None, type=str)
    point = request.args.get("point", None)
    id = request.args.get("id", None)
    update_by = request.args.get("update_by", None)
    if update_by == None:
        return f"update_by must be filled\n\nYou must fill update_by parameter and one of them (first_name, last_name, subject, point) in order to update row. if you want to insert new row fill everything. \n Parameters:\nfirst_name string,\nlast_name string,\nsubject string,\npoint float,\nid integer,\nupdate_by can be set first_name, last_name, subject, point, id, insert\n"
    elif update_by == "first_name" and first_name == None:
        return f"{update_by} must be filled\n\nYou must fill update_by parameter and one of them (first_name, last_name, subject, point) in order to update row. if you want to insert new row fill everything. \n Parameters:\nfirst_name string,\nlast_name string,\nsubject string,\npoint float,\nid integer,\nupdate_by can be set first_name, last_name, subject, point, id, insert\n"
    elif update_by == "last_name" and last_name == None:
        return f"{update_by} must be filled\n\nYou must fill update_by parameter and one of them (first_name, last_name, subject, point) in order to update row. if you want to insert new row fill everything. \n Parameters:\nfirst_name string,\nlast_name string,\nsubject string,\npoint float,\nid integer,\nupdate_by can be set first_name, last_name, subject, point, id, insert\n"
    elif update_by == "subject" and subject == None:
        return f"{update_by} must be filled\n\nYou must fill update_by parameter and one of them (first_name, last_name, subject, point) in order to update row. if you want to insert new row fill everything. \n Parameters:\nfirst_name string,\nlast_name string,\nsubject string,\npoint float,\nid integer,\nupdate_by can be set first_name, last_name, subject, point, id, insert\n"
    elif update_by == "point" and point == None:
        return f"{update_by} must be filled\n\nYou must fill update_by parameter and one of them (first_name, last_name, subject, point) in order to update row. if you want to insert new row fill everything. \n Parameters:\nfirst_name string,\nlast_name string,\nsubject string,\npoint float,\nid integer,\nupdate_by can be set first_name, last_name, subject, point, id, insert\n"
    elif update_by == "id" and id == None:
        return f"{update_by} must be filled\n\nYou must fill update_by parameter and one of them (first_name, last_name, subject, point) in order to update row. if you want to insert new row fill everything. \n Parameters:\nfirst_name string,\nlast_name string,\nsubject string,\npoint float,\nid integer,\nupdate_by can be set first_name, last_name, subject, point, id, insert\n"
    elif update_by == "insert":
        if first_name == None or last_name == None or subject == None or point == None:
            return f"first_name, last_name, subject, point must be filled!!!\n\nYou must fill update_by parameter and one of them (first_name, last_name, subject, point) in order to update row. if you want to insert new row fill everything. \n Parameters:\nfirst_name string,\nlast_name string,\nsubject string,\npoint float,\nid integer,\nupdate_by can be set first_name, last_name, subject, point, id, insert\n"
        elif len(first_name.strip())==0:
            return f"First name must be filled"
        elif len(last_name.strip())==0:
            return f"Last name must be filled"
        elif len(subject.strip())==0:
            return f"Subject must be filled"
        elif len(str(point).strip())==0:
            return f"Point must be filled"
        else:
            try:
                point = float(point)
            except ValueError:
                return "Point must be float"
            except:
                return "Something went wrong"
    if update_by not in ['first_name', 'last_name', 'subject', 'point', 'id','insert']:
        return "Incorrect update_by values"
    if update_by == "id":
         try:
             id = int(id)
         except ValueError:
             return "id must be integer"
         except:
             return "Something went wrong"

    resp = for_delete.update({"first_name":first_name,"last_name":last_name,"subject":subject,"point":point,"id":id},update_by)
    return resp


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="80",debug=True)
