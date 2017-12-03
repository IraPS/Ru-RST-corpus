from py2neo import Graph
import itertools
import operator

graph = Graph()  # creating a graph for a database

# кажддый "реальный" node имеет "Id", "Text_id", "text", "lemmas". Т.е. достаточно проверить, есть ли у node "text",
# если есть, по нему можно искать. Если нет - то это фиктивный node, который появился в результате объединения ЭДЕ.

# nodes = graph.find('EDU')
# real_edus = [node for node in nodes if 'text' in node]


def search_edus(parameter, value):
    found = None
    if parameter == 'word':
        found = graph.run("MATCH (n) WHERE '" + value + "' in split(n.text, ' ')\n RETURN n.Text_id, split(n.text, ' ')")
        found = [[n[0], n[1]] for n in found]
    if parameter == 'lemma':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, split(n.text, ' ')")
        found = [[n[0], n[1]] for n in found]
    if parameter == 'pos':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, split(n.text, ' ')")
        found = [[n[0], n[1]] for n in found]
    # print([n for n in found if n[0] == 20], '\n\n')
    if found:
        found.sort(key=operator.itemgetter(0))
        found_by_text = itertools.groupby(found, lambda x: x[0])
        found = found_by_text
    return found

'''
search_result = search_edus('word', 'в')
for i, l in search_result:
    print(i, [n[1] for n in list(l)])
'''


