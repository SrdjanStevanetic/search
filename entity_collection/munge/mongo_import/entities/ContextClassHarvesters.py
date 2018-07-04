class LanguageValidator:
    import sys, os
    # TODO: What to do with weird 'def' language tags all over the place?
    LOG_LOCATION = os.path.join(os.path.dirname(__file__), '..', 'logs', 'langlogs')

    def __init__(self):
        import os
        self.langmap = {}
        langlistloc = os.path.join(os.path.dirname(__file__), '..', 'all_langs.wkp')
        with open(langlistloc, 'r', encoding="UTF-8") as all_langs:
            for lang in all_langs:
                if(not(lang.startswith("#")) and ("|" in lang)):
                    (name, code) = lang.split('|')
                    self.langmap[code.strip()] = name

    def validate_lang_code(self, entity_id, code):
       if(code in self.langmap.keys()):
           return True
       elif(code == 'def'):
           # TODO: sort out the 'def' mess at some point
           self.log_invalid_lang_code(entity_id, 'def')
           return True
       elif(code == ''):
           self.log_invalid_lang_code(entity_id, 'Empty string')
           return True
       else:
           self.log_invalid_lang_code(entity_id, code)
           return False

    def pure_validate_lang_code(self, code):
       if(code in self.langmap.keys()):
           return True
       elif(code == 'def'):
           return True
       else:
           return False

    def log_invalid_lang_code(self, entity_id, code):
        # TODO: differentiate logfiles by date
        filename = "logs.txt"
        filepath = LanguageValidator.LOG_LOCATION + filename
        with open(filepath, 'a') as lgout:
            msg = "Invalid language code found on entity " + str(entity_id) + ": " + str(code)
            lgout.write(msg)
            lgout.write("\n")

    def print_langs(self):
        print(self.langmap)


class ContextClassHarvester:

    import os

    DEFAULT_CONFIG_SECTION = 'CONFIG'
    HARVESTER_MONGO_HOST = 'harvester.mongo.host'
    HARVESTER_MONGO_PORT = 'harvester.mongo.port'
    
    ORGHARVESTER_MONGO_HOST = 'organization.harvester.mongo.host'
    ORGHARVESTER_MONGO_PORT = 'organization.harvester.mongo.port'
    
    CHUNK_SIZE = 250   # each file will consist of 250 entities
    WRITEDIR = os.path.join(os.path.dirname(__file__), '..', 'entities_out')
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
    LANG_VALIDATOR = LanguageValidator()
    LOG_LOCATION = 'logs/entlogs/'
    
    DC_IDENTIFIER = 'dc_identifier'
    ORGANIZATION_DOMAIN = 'organizationDomain'
    EUROPEANA_ROLE = 'europeanaRole'
    GEOGRAPHIC_LEVEL = 'geographicLevel'
    COUNTRY = 'country'
    
    FIELD_MAP = {
        # maps mongo fields to their solr equivalents
        # TODO: there are numerous fields defined in the schema but not 
        # found in the actual data. They are accordingly not represented here.
        # For a list of all fields that might conceivably exist in accordance
        # with the data model, see https://docs.google.com/spreadsheets/d/
        #           1b1UN27M2eCia0L54di0KQY7KcndTq8-wxzwM4wN-8DU/edit#gid=340708208
        'prefLabel' : { 'label' : 'skos_prefLabel' , 'type' : 'string' },
        'altLabel' : { 'label': 'skos_altLabel' , 'type' : 'string' },
        'hiddenLabel' : { 'label' : 'skos_hiddenLabel', 'type' : 'string'},
        'edmAcronym' : { 'label' : 'edm_acronym', 'type' : 'string'},
        'note' : { 'label': 'skos_note' , 'type' : 'string' },
        'begin' : { 'label' : 'edm_begin', 'type' : 'string'},
        'end' : { 'label' : 'edm_end', 'type' : 'string'}, 
        'owlSameAs' : { 'label': 'owl_sameAs' , 'type' : 'ref' },
        'edmIsRelatedTo' : { 'label': 'edm_isRelatedTo' , 'type' : 'ref' },
        'dcIdentifier' : { 'label': DC_IDENTIFIER , 'type' : 'string' },
        'dcDescription' : { 'label': 'dc_description' , 'type' : 'string' },
        'rdaGr2DateOfBirth' : { 'label': 'rdagr2_dateOfBirth' , 'type' : 'string' },
        #not used yet
        #'rdaGr2DateOfEstablishment' : { 'label': 'rdagr2_dateOfEstablishment' , 'type' : 'string' },
        'rdaGr2DateOfDeath' : { 'label': 'rdagr2_dateOfDeath' , 'type' : 'string' },
        #not used yet
        #'rdaGr2DateOfTermination' : { 'label': 'rdagr2_dateOfTermination' , 'type' : 'string' },
        'rdaGr2PlaceOfBirth' : { 'label': 'rdagr2_placeOfBirth' , 'type' : 'string' },
        'placeOfBirth' : { 'label': 'rdagr2_placeOfBirth' , 'type' : 'string' },
        #not used yet
        #'placeOfBirth_uri' : { 'label': 'rdagr2_placeOfBirth.uri' , 'type' : 'string' },
        'rdaGr2PlaceOfDeath' : { 'label': 'rdagr2_placeOfDeath' , 'type' : 'string' },
        #not used yet
        #'placeOfDeath_uri' : { 'label': 'rdagr2_placeOfDeath.uri' , 'type' : 'string' },
        'rdaGr2PlaceOfDeath' : { 'label': 'rdagr2_placeOfDeath' , 'type' : 'string' },
        #not used yet
        #'professionOrOccupation_uri' : { 'label': 'professionOrOccupation.uri' , 'type' : 'string' },
        'rdaGr2ProfessionOrOccupation' :  { 'label': 'rdagr2_professionOrOccupation' , 'type' : 'string' },
        #not used yet
        #'gender' : { 'label': 'gender' , 'type' : 'string' },
        'rdaGr2BiographicalInformation' : { 'label': 'rdagr2_biographicalInformation' , 'type' : 'string' },
        'latitude' : { 'label': 'wgs84_pos_lat' , 'type' : 'string' },
        'longitude' : { 'label': 'wgs84_pos_long' , 'type' : 'string' },
        'begin' : { 'label': 'edm_begin' , 'type' : 'string' },
        #not used yet
        #'beginDate' : { 'label': 'edm_beginDate' , 'type' : 'string' },
        'end' : { 'label': 'edm_end' , 'type' : 'string' },
        #not used yet
        #'endDate' : { 'label': 'edm_endDate' , 'type' : 'string' },
        'isPartOf' : { 'label': 'dcterms_isPartOf' , 'type' : 'ref' },
        'hasPart' : { 'label' : 'dcterms_hasPart', 'type' : 'ref'},
        'hasMet' : { 'label' : 'edm_hasMet', 'type' : 'ref' },
        'date' : { 'label' : 'dc_date', 'type' : 'string' },
        'exactMatch': { 'label' :  'skos_exactMatch', 'type' : 'string' },
        'related' : { 'label' : 'skos_related', 'type' : 'ref'  },
        'broader' : { 'label' : 'skos_broader', 'type' : 'ref'},
        'narrower' : { 'label' : 'skos_narrower', 'type' : 'ref'},
        'related' : { 'label' : 'skos_related', 'type' : 'ref'},
        'broadMatch' : { 'label' : 'skos_broadMatch', 'type' : 'ref'},
        'narrowMatch' : { 'label' : 'skos_narrowMatch', 'type' : 'ref' },
        'relatedMatch' : { 'label' : 'skos_relatedMatch', 'type' : 'ref' },
        'exactMatch' : { 'label' : 'skos_exactMatch', 'type' : 'ref' },
        'closeMatch' : { 'label' : 'skos_closeMatch', 'type' : 'ref' },
        'notation' : { 'label' : 'skos_notation', 'type' : 'ref' },
        'inScheme' : { 'label' : 'skos_inScheme', 'type' : 'ref' },
        'note' : { 'label' : 'skos_note', 'type' : 'string' },
        'foafLogo' : { 'label' : 'foaf_logo', 'type' : 'ref' },
        # not used yet
        #name' : { 'label' : 'foaf_name', 'type' : 'string' },
        'foafHomepage' : { 'label' : 'foaf_homepage', 'type' : 'ref'},
        'edmEuropeanaRole' : { 'label' : EUROPEANA_ROLE, 'type' : 'string'},
        'edmOrganizationDomain' : { 'label' : ORGANIZATION_DOMAIN, 'type' : 'string'},
        #TODO: remove, not supported anymore
        #'edmOrganizationSector' : { 'label' : 'edm_organizationSector', 'type' : 'string'},
        #'edmOrganizationScope' : { 'label' : 'edm_organizationScope', 'type' : 'string'},
        'edmGeographicLevel' : { 'label' : GEOGRAPHIC_LEVEL, 'type' : 'string'},
        'edmCountry' : { 'label' : COUNTRY, 'type' : 'string'},
        'address_about' : { 'label' : 'vcard_hasAddress', 'type' : 'string'},
        'vcardStreetAddress' : { 'label' : 'vcard_streetAddress', 'type' : 'string'},
        'vcardLocality' : { 'label' : 'vcard_locality', 'type' : 'string' },
        'vcardPostalCode' : { 'label' : 'vcard_postalCode', 'type' : 'string'},
        'vcardCountryName' : { 'label' : 'vcard_countryName', 'type' : 'string' },
        'vcardPostOfficeBox' : { 'label' : 'vcard_postOfficeBox', 'type' : 'string'}
    }

    def log_warm_message(self, entity_id, message):
        # TODO: differentiate logfiles by date
        filename = "warn.txt"
        filepath = LanguageValidator.LOG_LOCATION + filename
        with open(filepath, 'a') as lgout:
            msg = "Warning info on processing entity " + str(entity_id) + ": " + str(message)
            lgout.write(msg)
            lgout.write("\n")

    # TODO: add address processing

    def __init__(self, name, entity_class):
        from pymongo import MongoClient
        from configparser import RawConfigParser 
        import sys, os 
        import RelevanceCounter
        import PreviewBuilder
        import HarvesterConfig
        
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'preview_builder'))
        
        self.config = HarvesterConfig.HarvesterConfig()
        self.mongo_entity_class = entity_class
        self.name = name
        self.client = MongoClient(self.get_mongo_host(), self.get_mongo_port())
        self.write_dir = ContextClassHarvester.WRITEDIR + "/" + self.name
        self.preview_builder = PreviewBuilder.PreviewBuilder(self.client)
        
    def get_mongo_host (self):
        #return default mongo host, the subclasses may use the type based config (e.g. see organizations)
        return self.config.get_mongo_host() 
        
    def get_mongo_port (self):
        #return default mongo port, the subclasses may use the type based config (e.g. see also organizations host)
        return self.config.get_mongo_port()
        
    def build_solr_doc(self, entities, start):
        from xml.etree import ElementTree as ET

        docroot = ET.Element('add')
        for entity_id, values  in entities.items():
            print("processing entity:" + entity_id)
            self.build_entity_doc(docroot, entity_id, values)
        self.client.close()
        return self.write_to_file(docroot, start)

    def add_field(self, docroot, field_name, field_value):
        from xml.etree import ElementTree as ET

        f = ET.SubElement(docroot, 'field')
        f.set('name', field_name)
        try:
            f.text = self.sanitize_field(field_value)
        except Exception as ex:
            print(str(field_name) + "!" + str(field_value) + str(ex))

    def sanitize_field(self, field_value):
        field_value = field_value.replace("\n", " ")
        field_value = field_value.replace("\\n", " ")
        field_value = field_value.replace("\t", " ")
        return field_value

    def write_to_file(self, doc, start):
        from xml.etree import ElementTree as ET
        from xml.dom import minidom
        import io
        writepath = self.get_writepath(start)
        roughstring = ET.tostring(doc, encoding='utf-8')
        reparsed = minidom.parseString(roughstring)
        reparsed = reparsed.toprettyxml(encoding='utf-8', indent="     ").decode('utf-8')
        with io.open(writepath, 'w', encoding='utf-8') as writefile:
            writefile.write(reparsed)
            writefile.close()
        return writepath

    def get_writepath(self, start):
        return self.write_dir + "/" + self.name + "_" + str(start) + "_" + str(start + ContextClassHarvester.CHUNK_SIZE) +  ".xml"

    def grab_relevance_ratings(self, docroot, entity_id, entity_rows):
        hitcounts = self.relevance_counter.get_raw_relevance_metrics(entity_id, entity_rows)
        eu_enrichments = hitcounts["europeana_enrichment_hits"]
        eu_terms = hitcounts["europeana_string_hits"]
        pagerank = hitcounts["pagerank"]
        ds = self.relevance_counter.calculate_relevance_score(entity_id, pagerank, eu_enrichments, eu_terms)
        self.add_field(docroot, 'europeana_doc_count', str(eu_enrichments))
        self.add_field(docroot, 'europeana_term_hits', str(eu_terms))
        self.add_field(docroot, 'pagerank', str(pagerank))
        self.add_field(docroot, 'derived_score', str(ds))
        self.add_suggest_filters(docroot, eu_terms)
        return True

    def process_address(self, docroot, entity_id, address):
        #TODO check if the full address is needed
        #address_components = []
        for k, v in address.items():
            key = k	
            if ("about" == k):
                key = "address_" + k
            if(key not in ContextClassHarvester.FIELD_MAP.keys()):
                self.log_warm_message(entity_id, "unmapped field: " + key)
                continue
            
            field_name = ContextClassHarvester.FIELD_MAP[key]['label']
            field_name = field_name + ".1"
            self.add_field(docroot, field_name, v)
            #address_components.append(v)

        #if(len(address_components) > 0):
        #    self.add_field(docroot, "vcard_fulladdresskey...", ",".join(address_components))

    def process_representation(self, docroot, entity_id, entity_rows):
        # TODO: Refactor to shrink this method
        import json
        #all pref labels
        all_preflabels = []
        for characteristic in entity_rows['representation']:
            if(characteristic == "address"):
                self.process_address(docroot, entity_id, entity_rows['representation']['address']['AddressImpl'])
            elif str(characteristic) not in ContextClassHarvester.FIELD_MAP.keys():
                # TODO: log this?
                print("unmapped property: " + str(characteristic))
                continue
            # TODO: Refactor horrible conditional
            elif(str(characteristic) == "dcIdentifier"):
                self.add_field(docroot, ContextClassHarvester.DC_IDENTIFIER, entity_rows['representation']['dcIdentifier']['def'][0])
            elif(str(characteristic) == "edmOrganizationDomain"):
                #TODO: create method to add solr field for .en fields
                self.add_field(docroot, ContextClassHarvester.ORGANIZATION_DOMAIN + ".en", entity_rows['representation']['edmOrganizationDomain']['en'])
            elif(str(characteristic) == "edmEuropeanaRole"):
                self.add_field(docroot, ContextClassHarvester.EUROPEANA_ROLE + ".en", entity_rows['representation']['edmEuropeanaRole']['en'])
            elif(str(characteristic) == "edmGeographicLevel"):
                self.add_field(docroot, ContextClassHarvester.GEOGRAPHIC_LEVEL + ".en", entity_rows['representation']['edmGeographicLevel']['en'])
            elif(str(characteristic) == "edmCountry"):
                self.add_field(docroot, ContextClassHarvester.COUNTRY, entity_rows['representation']['edmCountry']['en'])
            #not supported anymore 
            #elif(str(characteristic) == "edmOrganizationSector"):
            #    self.add_field(docroot, "edm_organizationSector.en", entity_rows['representation']['edmOrganizationSector']['en'])
            #elif(str(characteristic) == "edmOrganizationScope"):
            #    self.add_field(docroot, "edm_organizationScope.en", entity_rows['representation']['edmOrganizationScope']['en'])            
            # if the entry is a dictionary (language map), then the keys should be language codes
            elif(type(entity_rows['representation'][characteristic]) is dict):
                #for each entry in the language map
                for lang in entity_rows['representation'][characteristic]:
                    pref_label_count = 0
                    #avoid duplicates when adding values from prefLabel
                    prev_alts = []
                    if(ContextClassHarvester.LANG_VALIDATOR.validate_lang_code(entity_id, lang)):
                        field_name = ContextClassHarvester.FIELD_MAP[characteristic]['label']
                        field_values = entity_rows['representation'][characteristic][lang]
                        #property is language map of strings
                        if(type(field_values) == str):
                            unq_name = lang if lang != 'def' else ''
                            q_field_name = field_name + "."+ unq_name
                            #field value = field_values
                            self.add_field(docroot, q_field_name, field_values) 
                        else:
                            #for each value in the list
                            for field_value in field_values:
                                q_field_name = field_name
                                unq_name = lang if lang != 'def' else ''
                                if(ContextClassHarvester.FIELD_MAP[characteristic]['type'] == 'string'):
                                    q_field_name = field_name + "."+ unq_name
                                # Code snarl: we often have more than one prefLabel per language in the data
                                # We can also have altLabels
                                # We want to shunt all but the first-encountered prefLabel into the altLabel field
                                # while ensuring the altLabels are individually unique
                                # TODO: Refactor (though note that this is a non-trivial refactoring)
                                if(characteristic == 'prefLabel' and pref_label_count > 0):
                                    #move all additional labels to alt label
                                    q_field_name = "skos_altLabel." + unq_name
                                    #SG - TODO: add dropped pref labels to prev_alts??
                                    #prev_alts.append(field_value)
                                if('altLabel' in q_field_name):
                                    #TODO: SG why this? we skip alt labels here, but we don't add the gained entries from prefLabels
                                    if(field_value in prev_alts):
                                        continue
                                    prev_alts.append(field_value)
                                    #suggester uses alt labels for some entity types (organizations) 
                                    self.add_alt_label_to_suggest(field_value, all_preflabels)
                                if(str(characteristic) == "edmAcronym"):
                                    #suggester uses alt labels for some entity types (organizations) 
                                    self.add_acronym_to_suggest(field_value, all_preflabels)
                                    
                                if(characteristic == 'prefLabel' and pref_label_count == 0):
                                    pref_label_count = 1
                                    #TODO: SG - the suggester could actually make use of all pref labels, but the hightlighter might crash
                                    all_preflabels.append(field_value)
                                
                                #add field to solr doc
                                self.add_field(docroot, q_field_name, field_value)                                                          
            #property is list
            elif(type(entity_rows['representation'][characteristic]) is list):
                field_name = ContextClassHarvester.FIELD_MAP[characteristic]['label']
                for entry in entity_rows['representation'][characteristic]:
                    self.add_field(docroot, field_name, entry)
            # property is a single value
            else: 
                try:
                    field_name = ContextClassHarvester.FIELD_MAP[characteristic]['label']
                    field_value = entity_rows['representation'][characteristic]
                    self.add_field(docroot, field_name, str(field_value))
                except KeyError as ke:
                    print('Attribute ' + field_name + ' found in source but undefined in schema.')
        #add suggester payload
        payload = self.build_payload(entity_id, entity_rows)
        self.add_field(docroot, 'payload', json.dumps(payload))
        #add suggester field
        all_preflabels = self.shingle_preflabels(all_preflabels)
        # SG: values in the same language are joined using space separator. underscore is not really needed 
        #self.add_field(docroot, 'skos_prefLabel', "_".join(sorted(set(all_preflabels))))
        self.add_field(docroot, 'skos_prefLabel', " ".join(sorted(set(all_preflabels))))
        depiction = self.preview_builder.get_depiction(entity_id)
        if(depiction):
            self.add_field(docroot, 'foaf_depiction', depiction)
        self.grab_relevance_ratings(docroot, entity_id, entity_rows['representation'])

    def shingle_preflabels(self, preflabels):
        shingled_labels = []
        for label in preflabels:
            all_terms = label.split()
            for i in range(len(all_terms)):
                shingle = " ".join(all_terms[i:len(all_terms)])
                shingled_labels.append(shingle)
        return shingled_labels

    def build_payload(self, entity_id, entity_rows):
        import json
        entity_type = entity_rows['entityType'].replace('Impl', '')
        payload = self.preview_builder.build_preview(entity_type, entity_id, entity_rows['representation'])
        return payload

    def add_suggest_filters(self, docroot, term_hits):
        entity_type = self.name[0:len(self.name) - 1].capitalize()
        self.add_field(docroot, 'suggest_filters', entity_type)
        if(term_hits > 0):
            self.add_field(docroot, 'suggest_filters', 'in_europeana')
    
    def suggest_by_alt_label(self):
        #this functionality can be activated by individual harvesters
        return False
    
    def suggest_by_acronym(self):
        #this functionality can be activated by individual harvesters
        return False
        
    def add_alt_label_to_suggest(self, value, suggester_values):
        if(self.suggest_by_alt_label() and (value not in suggester_values)):
            suggester_values.append(value)
            
    def add_acronym_to_suggest(self, value, suggester_values):
        if(self.suggest_by_acronym() and (value not in suggester_values)):
            suggester_values.append(value)
    
class ConceptHarvester(ContextClassHarvester):

    def __init__(self):
        import sys, os
        ContextClassHarvester.__init__(self, 'concepts', 'eu.europeana.corelib.solr.entity.ConceptImpl')
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        self.relevance_counter = RelevanceCounter.ConceptRelevanceCounter()

    def get_entity_count(self):
        concepts = self.client.annocultor_db.concept.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/concept/base).*$' }} )
        return len(concepts)

    def build_entity_chunk(self, start):
        concepts = self.client.annocultor_db.concept.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/concept/base).*$' }} )[start:start + ContextClassHarvester.CHUNK_SIZE]
        concepts_chunk = {}
        for concept in concepts:
            concepts_chunk[concept] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : concept })
        return concepts_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        doc = ET.SubElement(docroot, 'doc')
        uri = entity_rows['codeUri']
        self.add_field(doc, 'id', uri)
        self.add_field(doc, 'internal_type', 'Concept')
        self.process_representation(doc, uri, entity_rows)

class AgentHarvester(ContextClassHarvester):

    def __init__(self):
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'agents', 'eu.europeana.corelib.solr.entity.AgentImpl')
        self.relevance_counter = RelevanceCounter.AgentRelevanceCounter()

    def get_entity_count(self):
        agents = self.client.annocultor_db.people.distinct( 'codeUri' )
        return len(agents)

    def build_entity_chunk(self, start):
        agents = self.client.annocultor_db.people.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        agents_chunk = {}
        for agent in agents:
            agents_chunk[agent] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : agent })
        return agents_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        if(entity_rows is None):
            self.log_missing_entry(entity_id)
            return
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        id = entity_id
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', id)
        self.add_field(doc, 'internal_type', 'Agent')
        self.process_representation(doc, entity_id, entity_rows)

    def log_missing_entry(self, entity_id):
        msg = "Entity found in Agents but not TermList collection: " + entity_id
        logfile = "missing_agents.txt"
        logpath = ContextClassHarvester.LOG_LOCATION + logfile
        with open(logpath, 'a') as lgout:
            lgout.write(msg)
            lgout.write("\n")

class PlaceHarvester(ContextClassHarvester):

    def __init__(self):
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'places', 'eu.europeana.corelib.solr.entity.PlaceImpl')
        self.relevance_counter = RelevanceCounter.PlaceRelevanceCounter()

    def get_entity_count(self):
        place_list = self.client.annocultor_db.TermList.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/place/).*$' }} )
        return len(place_list)

    def build_entity_chunk(self, start):
        places = self.client.annocultor_db.place.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        places_chunk = {}
        for place in places:
            places_chunk[place] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : place })
        return places_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        id = entity_id
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', id)
        self.add_field(doc, 'internal_type', 'Place')
        self.process_representation(doc, entity_id, entity_rows)

class OrganizationHarvester(ContextClassHarvester):

    def __init__(self):
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'organizations', 'eu.europeana.corelib.solr.entity.OrganizationImpl')
        self.relevance_counter = RelevanceCounter.OrganizationRelevanceCounter()

    def get_mongo_host (self):
        return self.config.get_mongo_host(self.name)
     
    def suggest_by_alt_label(self):
        return True
    
    def suggest_by_acronym(self):
        return True
    
    def get_entity_count(self):
        org_list = self.client.annocultor_db.TermList.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/organization/).*$' }} )
        print("importing organizations: " + str(len(org_list)))
        return len(org_list)

    def build_entity_chunk(self, start):
        orgs = self.client.annocultor_db.organization.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        orgs_chunk = {}
        for org in orgs:
            orgs_chunk[org] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : org })
        return orgs_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        id = entity_id
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', id)
        self.add_field(doc, 'internal_type', 'Organization')
        self.process_representation(doc, entity_id, entity_rows)


class IndividualEntityBuilder:
    import os, shutil

    TESTDIR = os.path.join(os.path.dirname(__file__), '..', 'tests', 'testfiles', 'dynamic')

    def build_individual_entity(self, entity_id, is_test=False):
        from pymongo import MongoClient
        import os, shutil
        if(entity_id.find("/place/") > 0):
            harvester = PlaceHarvester()
        elif(entity_id.find("/agent/") > 0):
            harvester = AgentHarvester()
        elif(entity_id.find("/organization/") > 0):
            harvester = OrganizationHarvester()
        else:
            harvester = ConceptHarvester()
        
        self.client = MongoClient(harvester.get_mongo_host(), harvester.get_mongo_port())
        entity_rows = self.client.annocultor_db.TermList.find_one({ "codeUri" : entity_id })
        entity_chunk = {}
        entity_chunk[entity_id] = entity_rows
        rawtype = entity_rows['entityType']
        
        start = int(entity_id.split("/")[-1])
        harvester.build_solr_doc(entity_chunk, start)
        if(not(is_test)): print("Entity " + entity_id + " written to " + rawtype[0:-4].lower() + "_" + str(start) + ".xml file.")
        if(is_test):
            current_location = harvester.get_writepath(start)
            namebits = entity_id.split("/")
            newname = namebits[-3] + "_" + namebits[-1] + ".xml"
            shutil.copyfile(current_location, IndividualEntityBuilder.TESTDIR + "/" + newname)
            os.remove(current_location) # cleaning up
#        except Exception as e:
#            print("No entity with that ID found in database. " + str(e))
#            return

class ChunkBuilder:

    def __init__(self, entity_type, start):
        self.entity_type = entity_type.lower()
        self.start = start

    def build_chunk(self):
        harvester = ConceptHarvester()
        if(self.entity_type == "agent"):
            harvester = AgentHarvester()
        elif(self.entity_type == "place"):
            harvester = PlaceHarvester()
        elif(self.entity_type == "organization"):
            harvester = OrganizationHarvester()
        ec = harvester.build_entity_chunk(self.start)
        harvester.build_solr_doc(ec, self.start)
