import os, json

class Explorer:
    #fields
##    DIRS = ["documents", "videos", "pictures", "music"]   #holds paths to primary dirs to index
    ROOT = ""
    DIRS = ["documents", "videos", "pictures", "music", "downloads", "desktop"]   #holds paths to primary dirs to index
    CLASSES = ["video", "image", "audio", "document"]
    EXTENSIONS = {
        "video":['mp4', 'mkv', '3gp', 'avi'],
        "image":['jpg', 'png'],
        "audio":['mp3', 'm4a', 'wav'],
        "document":['docx', 'txt', 'pdf', 'ppt', 'epub']
        }

    FILE_CLASSES = {'video':[], 'image':[], 'audio':[], 'document':[]}
    KEYWORDS = {
        "music":"audio", "audio":"audio", "songs":"audio", "audios":"audio",
        "documents":"document", "docs":"document", "document":"document",
        "videos":"video", "video":"video", "movie":"video", "movies":"video",
        "pix":"image", "images":"image", "pics":"image", "image":"image", "pictures":"image"
        }

    FILE_PROPERTIES = {
        "dir=":"dir=", "indir=":"indir="
        }
    
    FILES_INDEX = {}
    INDEX = {}
    INDEXX = {}
    INDEXXX = {}
    INDEX_LENGTH = -1
    
    def __init__(self):
        self.loadIndexes()
        result, cwd = None, None
        results = {}
        cwd_path = "root"
        
        print("="*190)
        print('{0: <80} '.format(" "), '{0: <10} '.format("Smart Explorer"))
        print("="*190)
        print("help: type reindex to reindex the file contents, restart to clear working dir path")
        while True:
            echo = True
            text = input("\[{}]> ".format(cwd_path))
            if text.endswith(";"):
                echo = False
                text = text[:-1]
                
            if text in ["exit"]:
                break

            elif text in ["restart"]:
                result = None
                cwd_path = "root"

            elif text in ["reload", "reindex", "reload index"]:
                self.indexDirs()

            elif text in ["echo"]:
                self.displayResult(result)

            elif text in ["/"]:
                if cwd_path != "root":
                    del results[cwd_path]
                    cwd_path = " > ".join(cwd_path.split(" > ")[:-1])
                    print(cwd_path, {x:len(results[x].values()) for x in results})
                    if cwd_path == "root":
                        result, cwd = None, None

                    else:
                        cwd = results[cwd_path].copy()
                
            else:
                result = self.search(text, cwd)
                if len(result) > 0:
                    cwd = result
                    if cwd_path.split(" > ")[-1] != text:
                        cwd_path += " > "+text
                    results.setdefault(cwd_path, result.copy())
                    if echo:
                        self.displayResult(result)
            print()
            
    def classifyFile(self, file):
        fileExtension = os.path.splitext(file)[-1][1:]
        CLASS = "other"
        for CLASS in self.CLASSES:
            if fileExtension in self.EXTENSIONS[CLASS]:
                break
        return CLASS

    def displayResult(self, result):
        if result == None:
            pass

        else:
            if len(result) in range(1, 111, 1):
                print("="*190)
                print('{0: <80} | {1: <7} | {2: <5} | {3: <50.50} '.format("Filename", "Type", "Size", "Directories"))
                print("="*190)
                
                for x in result:
                    print(
                        '{0: <80} | {1: <7} | {2: <5} | {3: <80.80} '.format(
                         x, result[x]["type"], "size", ", ".join(['%s'%(self.decodePath(dx).split("\\")[-1]) for dx in result[x]["dirs"]])))
                        
    def indexDirs(self, dirs=None):
##------------reinitialize index database
        self.INDEX = {}
        self.INDEXX = {}
        self.INDEXXX = {}
        self.FILES_INDEX = {}
        
        print("reindexing...")
        if dirs == None:
            dirs = self.DIRS

        #the primary or root dirs to be indexed
        for DIR in dirs:
            self.indexFiles(DIR)

        #prints out the files indexed 
##        for x in self.FILES_INDEX:
##            print(x, self.FILES_INDEX[x])

        self.writeJson('files_index', self.FILES_INDEX)
        print("Done!", sep="\n")
        
    #spider
    def indexFiles(self, path):
        for r, d, f in os.walk(path):
            
            rxx = r
            rx = r.split("\\")
            pre_dir, curr_dir = "\\".join(rx[:-1]).strip(), rx[-1]
            if pre_dir != self.ROOT:
                pre_dir_id = self.INDEXXX[pre_dir]                              
                    
                if curr_dir not in self.FILES_INDEX:
                    self.FILES_INDEX.setdefault(curr_dir, {"dirs":[pre_dir_id], "type":"folder"})

                else:
                    if pre_dir_id not in self.FILES_INDEX[curr_dir]["dirs"]:
                        self.FILES_INDEX[curr_dir]["dirs"].append(pre_dir_id)

            if len(rx) > len(self.ROOT.split("\\"))+1:
                ri = str(self.INDEXX[self.INDEXXX[pre_dir]])
                rxx = json.dumps({ri:rx[-1]})

            if rxx not in self.INDEXX:
                self.INDEX_LENGTH += 1
                self.INDEX.setdefault(str(self.INDEX_LENGTH), rxx)
                self.INDEXX.setdefault(rxx, str(self.INDEX_LENGTH))
                self.INDEXXX.setdefault(r, rxx)
                
            for fx in f:
                file_type = self.classifyFile(fx)
                if fx not in self.FILES_INDEX:
                    self.FILES_INDEX.setdefault(fx, {"dirs":[str(self.INDEX_LENGTH)], "type":file_type})

                else:
                    if rxx not in self.FILES_INDEX[fx]["dirs"]:
                        self.FILES_INDEX[fx]["dirs"].append(rxx)

                    
        self.writeJson('index', self.INDEX)
        self.writeJson('indexx', self.INDEXX)
        self.writeJson('indexxx', self.INDEXXX)

    def decodePath(self, path):
        try:
            val = json.loads(path)
            for x in val:
                if val[x] != x:
                    return self.decodePath(x)+"\\"+val[x]

                else:
                    return x

        except Exception as e:
            if path in self.INDEX:
                return self.decodePath(self.INDEX[path])

            else:
                return path
            
    def loadIndexes(self):
        self.INDEX = self.readJson('index')
        self.INDEXX = self.readJson('indexx')
        self.INDEXXX = self.readJson('indexxx')

        self.FILES_INDEX = self.readJson('files_index')
        
    def readJson(self, name):
        self.setup(name)
        
        file = open(name+'.json', 'r')
        content = file.read()
        file.close()
        return json.loads(content)

    def search(self, text, cwd=None):
        if cwd == None:
            cwd = self.FILES_INDEX.copy()
            
        search_params = []
        result = {}
        if text in self.KEYWORDS:
            search_params.append((self.KEYWORDS[text], "type"))
            
        for prop in self.FILE_PROPERTIES:
            if text.startswith(prop):
                xx = text.replace(prop, '', 1)
                search_params.append((xx, prop))

        if len(search_params) < 1:
            search_params.append((text, "in-text"))
            rst = {}
            
        #print(search_params)
        for file in cwd:
            for sx in search_params:
                if sx[-1] == "in-text":
                    if sx[0].lower() in file.lower():
                        if file not in result:
                            result.setdefault(file, cwd[file])

                    for dx in cwd[file]["dirs"]:
                        px = self.decodePath(dx)
                        if sx[0].lower() in px.lower():
                            if file not in rst:
                                rst.setdefault(file, cwd[file])
                                
                elif sx[-1] == "indir=" or sx[-1] == "dir=":
                    for dx in cwd[file]["dirs"]:
                        px = self.decodePath(dx)
                        if sx[-1] == "dir=" and sx[0].lower() in px.lower().split("\\"):
                            if file not in result:
                                result.setdefault(file, cwd[file])
                                
                            break

                        if sx[-1] == "indir=" and sx[0].lower() in px.lower():
                            if file not in result:
                                result.setdefault(file, cwd[file])
                            
                else:
                    if cwd[file][sx[-1]] == sx[0]:
                        if file not in result:
                            result.setdefault(file, cwd[file])
        #print(result)
        if len(result) < 1:
            result = rst
        return result.copy()
    
    def setup(self, name):
        if os.path.exists(os.getcwd()+"/"+name+".json"):
            pass

        else:
            self.writeJson(name, {})
            
    def writeJson(self, name, dictionary):
        content = json.dumps(dictionary)
        file = open(name+'.json', 'w')
        file.write(content)
        file.close()
        
if __name__ == '__main__':
    explorer_object = Explorer()    
