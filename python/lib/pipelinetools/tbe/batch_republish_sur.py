from tbe_coffer.session import session

palette_publishes = session.data.query(schema.Publish).filter(schema.Publish.process=="sur", 
    schema.Publish.component=="palette", schema.Publish.name==like("%s_look"))

