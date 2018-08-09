campus_info = {"campuses":[{"leaf":2, "spine":3},{"leaf":2, "spine":3},{"leaf":2, "spine":2}]}
'''
ports_map = { "1" => [1,2,3],
              "2" => [3,4,5],
              "3" => [1,4],
              "4" => [2,5]}
'''

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def per_campus(start,end,leaf,spine):
  links = leaf * spine
  total = leaf + spine

  dict = []
  for num in range(1,spine+1):
    spine_id = num
    spine_ports = range(num+start, links+1+start, spine)
    end_list = []
    end_list.append(end)
    if num % 2 == 0 and num != spine:
      end += 1
      end_list.append(end)
    spine_ports.extend(end_list)
    #dict.update({spine_id:spine_ports})
    dict.append(spine_ports)

  l_ports = list(chunks(range(1+start, links+1+start), spine))
  for num,ports in enumerate(l_ports):
    leaf_id = num + 1 + spine
    leaf_ports = ports
    #dict.update({leaf_id:leaf_ports})
    dict.append(leaf_ports)


  return dict

def between_spines(start,end,spine1,spine2):
  links = spine1 * spine2
  total = spine1 + spine2

  dict = []
  for num in range(1,spine+1):
    #spine_id = num
    spine_ports = range(num+start, links+1+start, spine)
    dict.append(spine_ports)

  l_ports = list(chunks(range(1+start, links+1+start), spine))
  for num,ports in enumerate(l_ports):
    leaf_id = num + 1 + spine
    leaf_ports = ports
    dict.append(leaf_ports)

  return dict

ports_map = {}

start = 0 
end = 0
ports = []
for campus in campus_info["campuses"]:
  leaf = campus["leaf"]
  spine = campus["spine"]
  total = leaf * spine
  end += total
  ports.extend(per_campus(start,end+1,leaf,spine))
  start +=  total + spine - 1
  end += spine - 1 

dev_num = 1
for port in ports:
  ports_map.update({dev_num:port})
  dev_num += 1

spine_list = []
couter = 1
for campus in campus_info["campuses"]:
  spine_list.append(campus["spine"])

counter = 1
spine_lst = []
spine_ports = []
for index,spine in enumerate(spine_list):
  if counter != len(campus_info["campuses"]):
    spine1 = spine_list[index]
    spine2 = spine_list[index+1]
    total = spine1 * spine2
    end += total
    ports1 = between_spines(start,end,spine1,spine2)
    spine_ports.extend(ports1)
    start += total
  counter += 1


spine_id_list = []
spine_counter = 0 
spine_count = 0
for index,campus in enumerate(campus_info["campuses"]):
  leaf = campus["leaf"]
  spine = campus["spine"]
  total = leaf + spine
  spine_id_lst = []
  for num in range(spine_counter+1,spine + spine_counter + 1,1):
    spine_counter = num
    spine_id_lst.append(spine_counter)
  spine_id_list.extend(spine_id_lst)
  spine_count += 1
  if spine_count % 2 == 0 and spine_count != len(campus_info["campuses"]):
    spine_id_list.extend(spine_id_lst)
  spine_counter += leaf
  
for spine_id,spine_port in zip(spine_id_list,spine_ports):
  ports_map[spine_id].extend(spine_port)

portsMap = ""
for ports in ports_map:
  print ports
  print ports_map[ports]
  if ports == 1:
    portsMap = '{"' + str(ports) + '"' + '=>' + str(ports_map[ports])
  else:
    portsMap = portsMap + ',' + '"' + str(ports) + '"' + '=>' + str(ports_map[ports])

print portsMap + '}'
