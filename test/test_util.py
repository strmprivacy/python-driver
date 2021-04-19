from strm.driver import current_time_millis
from strm.driver.domain import StreamMachineEvent
from strm.schema.avro.io.streammachine.schema.avro.strm_avro.v1 import StrmEvent
from strm.schema.json import SchemaJsonEvent, StrmMeta, Customer


class TestData(object):
    @staticmethod
    def create_avro_event() -> StreamMachineEvent:
        event = StrmEvent()
        event.abtests = ["abc"]
        event.customer.id = "integration-test"
        event.sessionId = "session-01"
        event.strmMeta.timestamp = current_time_millis()
        event.strmMeta.schemaId = "schema_avro"
        event.strmMeta.nonce = 1
        event.strmMeta.keyLink = 2
        event.strmMeta.consentLevels = [0, 1, 2]
        event.url = "bananas"
        return event

    @staticmethod
    def create_json_event() -> StreamMachineEvent:
        return SchemaJsonEvent(
            strmMeta=(StrmMeta(
                schemaId="schema_json",
                nonce=1,
                timestamp=current_time_millis(),
                keyLink=2,
                consentLevels=[0, 1, 2]
            )),
            sessionId="session-01",
            url="bananas",
            customer=(Customer(id="integration-test")),
            abtests=["abc"]
        )
