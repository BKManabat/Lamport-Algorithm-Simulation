from multiprocessing import Process, Manager
import random
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

plt.ioff()
# run the program, simulation images will be generated in /simulation_images folder with corresponding time

class Site:
  def __init__(self, id):
    self.queue = []
    self.id = id
    self.counter = 0
    self.cs_done = False
    self.permitted = False
    self.req = None

  def request(self):
    self.counter += 1
    self.req = (self.counter, self.id)
    self.queue.append(self.req)
    self.queue.sort()
    return self.req

  def receive_req(self, req):
    self.counter = max(self.counter, req[0])
    self.counter += 1
    self.queue.append(req)
    self.queue.sort()
    return (self.counter, self.id)

  def receive_reply(self, timestamps):
    self.counter = max([self.counter]+timestamps)
    if all(t > self.req[0] for t in timestamps):
      self.permitted = True

  def execute_cs(self):
    self.counter += 2
    if self.permitted and self.queue[0] == self.req:
      self.cs_done = True
      return self.queue.pop(0)
    return False
  
  def remove_req(self, to_rem, t):
    self.counter = max(self.counter, t)
    self.queue.remove(to_rem)
    self.counter += 1

  def __str__(self):
    return f"Site {self.id}"

def draw(sedges, img, psites=[], **kwargs):
  color_map = ['blue']*len(sedges)
  if 'on_cs' in kwargs:
    color_map[kwargs['on_cs']] = 'red'
  elif 'want' in kwargs:
    for site_id in kwargs['want']:
      color_map[site_id] = 'green'
  plt.clf()
  G = nx.Graph()
  G2 = nx.DiGraph()
  G.add_edges_from(sedges)
  red_edges = [] if 'red_edges' not in kwargs else kwargs['red_edges']
  black_edges = [edge for edge in G.edges() if edge not in red_edges]
  pos = nx.spring_layout(G)
  ax = plt.gca()
  ax.set_title(kwargs['log'])
  pos_attrs, sq = {}, {}
  for node, coords in pos.items():
    pos_attrs[node] = (coords[0], coords[1]-0.15)
  for site in psites:
    sq[site.id] = str(site.queue)
  nx.draw_networkx_labels(G, pos_attrs, labels=sq)
  nx.draw_networkx_edges(G2, pos, edgelist=red_edges, edge_color='r', arrows=True)
  if 'red_labels' in kwargs:
    nx.draw_networkx_edge_labels(G, pos, edge_labels=dict(zip(kwargs['red_edges'], kwargs['red_labels'])), font_color='red')
  nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=None)
  nx.draw(G, pos, node_color=color_map, with_labels=True)
  plt.savefig(f"static/assets/simulation_images/Time-{img}.png", bbox_inches='tight')


def simulate(sn):
  sites = [Site(i) for i in range(sn)]
  strings = []
  
  sedges = [(site.id, site.id+1) if site.id != len(sites)-1 else (site.id, 0) for site in sites] 
  draw(sedges, 0, psites=sites, log="Sites")

  manager = Manager()
  nvals = manager.list()
  nvals += [sites, strings]

  print("Generating simulation images...\n")
  while True:
    unfinished = [site for site in sites if not site.cs_done]
    if not unfinished:
      break
    req_sites = random.sample(unfinished, random.randint(1, len(unfinished)))
    want = [site.id for site in req_sites]
    log = f"Sites {want} are requesting to enter critical section"
    print(log)
    strings.append(log)
    nvals[1] = strings
    draw(sedges, max([site.counter for site in req_sites])+0.5, want=want, log=log)
    
    def request(requesting, pvals):
      psites, plogs = pvals[0], pvals[1]
      requesting = [site for site in psites if site.id == requesting.id][0]
      req = requesting.request()
      to_receive = [site for site in psites if site.id != requesting.id]
      replies, req_edges, rep_edges = [], [], []
      for receiving in to_receive:
        req_edges.append((requesting.id, receiving.id))
        rep_edges.append((receiving.id, requesting.id))
        replies.append(receiving.receive_req(req))
      rep_timestamps = [rep[0] for rep in replies]
      log = f"Time {requesting.counter}: {str(requesting)} has sent out a request message"
      print(log)
      plogs.append(log)

      draw(sedges, requesting.counter, red_edges=req_edges, log=log, psites=psites, red_labels=[req for i in range(len(req_edges))])
      log = f"Time {max(rep_timestamps)}: Sites {[site.id for site in to_receive]} have replied to {str(requesting)}'s request"
      print(log)
      plogs.append(log)
      
      draw(sedges, max(rep_timestamps), red_edges=rep_edges, log=log, psites=psites, red_labels=replies)
      requesting.receive_reply(rep_timestamps)
      pvals[0], pvals[1] = psites, plogs
      
    for requesting in req_sites:
      p = Process(target=request, args=(requesting, nvals))
      p.start()
      p.join()
      
    sites, strings = nvals[0], nvals[1]

    for executing in req_sites[:]:
      executed = sites[executing.id].execute_cs()
      if executed:
        log = f"Time {sites[executing.id].counter-1}: {str(executing)} has executed critical section"
        print(log)
        strings.append(log)
        
        draw(sedges, sites[executing.id].counter-1, psites=sites, on_cs=executing.id, log=log)
        rel_ids = [site.id for site in sites if site.id != executing.id]
        rel_edges = [(executing.id, id) for id in rel_ids]
        log = f"Time {sites[executing.id].counter}: {str(executing)} has sent out a release message"
        print(log)
        strings.append(log)
        
        draw(sedges, sites[executing.id].counter, psites=sites, red_edges=rel_edges, on_cs=executing.id, log=log, red_labels=[(sites[executing.id].counter, executed) for i in range(len(rel_edges))])
        for id in rel_ids:
          sites[id].remove_req(executed, sites[executing.id].counter)
        req_sites.remove(executing)
        log = f"Time {sites[rel_ids[0]].counter}: Sites {rel_ids} have released Site {executing.id}'s request'"
        print(log)
        strings.append(log)
        
        draw(sedges, sites[rel_ids[0]].counter, psites=sites, log=log)

    nvals[0], nvals[1] = sites, strings
    
  print("Simulation images generated.")

  with open("logs.json", "w") as file:
    json.dump(nvals[1], file)