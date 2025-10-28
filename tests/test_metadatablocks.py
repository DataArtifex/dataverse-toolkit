
def test_all_blocks(test_server):
    data = test_server.get_metadatablocks()
    print(data)
    assert data

def test_citation_block(test_server):
    data = test_server.get_metadatablock('citation')
    print(data)
    assert data
