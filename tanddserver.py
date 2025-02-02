import base64
import os
import pandas as pd
import struct

from dataclasses import dataclass
from flask import Flask, request
from xml.etree import ElementTree as ET

file_path = "log.csv"


@dataclass
class SensorMapping:
    temp_c: str = "13"
    rh: str = "208"

    def get_field_name(self, code: str) -> str:
        mapping = {self.temp_c: "temp_c", self.rh: "rh"}
        return mapping.get(code, "Unknown")


@dataclass
class SensorReading:
    unix_time: int
    serial: str
    sensor: str
    reading: float


app = Flask(__name__)

mapping = SensorMapping()


@app.route("/", methods=["POST"])
def handle_request():
    contains_xml = False

    for filename, file in request.files.items():
        try:
            file_content = file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            app.logger.warning(f"Failed to read {filename}: {e}")

        if "<?xml" in file_content:
            contains_xml = True

            xml_only = "<?xml" + file_content.split("<?xml", 1)[1]

            try:
                xml_root = ET.fromstring(xml_only)
            except Exception as e:
                app.logger.warning(f"Failed to build XML tree for {filename}: {e}")

            df_list = []

            try:
                device_serial = xml_root.find("./base/serial").text

                for ch in xml_root.findall(".//ch"):
                    record_type = ch.find("./record/type").text
                    record_start = int(ch.find("./record/unix_time").text)
                    record_count = int(ch.find("./record/count").text)
                    record_interval = int(ch.find("./record/interval").text)
                    record_data = ch.find("./record/data").text

                    decoded_bytes = base64.b64decode(record_data)
                    reading_list = list(
                        struct.unpack(
                            "<" + "h" * (len(decoded_bytes) // 2), decoded_bytes
                        )
                    )
                    reading_list = [(x - 1000) / 10.0 for x in reading_list]

                    timestamp_list = [
                        record_start + i * record_interval for i in range(record_count)
                    ]

                    sensor_readings = [
                        SensorReading(
                            unix_time=timestamp,
                            serial=device_serial,
                            sensor=mapping.get_field_name(record_type),
                            reading=reading,
                        )
                        for timestamp, reading in zip(timestamp_list, reading_list)
                    ]

                    df_list.append(
                        pd.DataFrame([reading.__dict__ for reading in sensor_readings])
                    )
            except Exception as e:
                app.logger.warning(f"Failed to parse {filename}: {e}")

            if len(df_list) > 0:
                try:
                    df = pd.concat(df_list)
                    df = df.sort_values("unix_time")
                except Exception as e:
                    app.logger.warning(f"Failed to concatenate and sort df_list: {e}")

                app.logger.info("Sensor readings")
                app.logger.info(df)

                if os.path.exists(file_path):
                    app.logger.info(f"Appending to {file_path}")
                    try:
                        df.to_csv(file_path, mode="a", header=False, index=False)
                    except Exception as e:
                        app.logger.warning(f"Failed to append to {file_path}: {e}")
                else:
                    app.logger.info(f"{file_path} does not exist, creating")
                    try:
                        df.to_csv(file_path, mode="w", header=True, index=False)
                    except Exception as e:
                        app.logger.warning(f"Failed to create {file_path}: {e}")
            else:
                app.logger.warning("No data found in XML")

    response_text = "R=3,0\r\n" if contains_xml else "R=2,0\r\n"

    return response_text, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
