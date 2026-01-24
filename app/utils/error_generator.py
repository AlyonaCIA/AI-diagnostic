"""
File: app/utils/error_generator.py
Description: Synthetic error generator for creating test cases and variations
of the two base error types (constant_error and empty_project).
"""

from dataclasses import dataclass
from typing import List, Tuple
import random


@dataclass
class SyntheticError:
    """Represents a synthetic error case with ground truth labels."""
    log_text: str
    xml_content: str
    expected_stage: str
    expected_severity: str
    expected_complexity: str
    error_type: str  # "constant_error" or "code_generation"


class ErrorGenerator:
    """Generates synthetic PLC error cases for testing and evaluation."""

    # Base templates for constant_error variations
    CONSTANT_ERROR_LOG_TEMPLATE = """[17:05:55]: Building project...
[17:05:56]: Cannot build project.
[17:05:56]: Cannot build project.
stdout: Warning: PLC XML file doesn't follow XSD schema at line 61:
Element '{{http://www.plcopen.org/xml/tc6_0201}}data': Missing child element(s). Expected is one of ( {{*}}*, * ).Start build in /tmp/.tmpMngQvj/build
Generating SoftPLC IEC-61131 ST/IL/SFC code...
Collecting data types
Collecting POUs
Generate POU program0
Generate Config(s)
Compiling IEC Program into C code...
0.000s 0.101s 0.201s 0.301s
"/root/beremiz/matiec/iec2c" -f -l -p -I "/root/beremiz/matiec/lib" -T "/tmp/.tmpMngQvj/build" "/tmp/.tmpMngQvj/build/plc.st"
Warning: exited with status 1 (pid 187)
0.342s
Warning: /tmp/.tmpMngQvj/build/plc.st:{line}-4..{line}-12: error: Assignment to CONSTANT variables is not allowed.
Warning: In section: PROGRAM program0
Warning: {line_formatted}: {assignment}
Warning: 1 error(s) found. Bailing out!
Warning:
Error: Error : IEC to C compiler returned 1
Error: PLC code generation failed !
"""

    CONSTANT_ERROR_XML_TEMPLATE = """<project xmlns="http://www.plcopen.org/xml/tc6_0201">
  <fileHeader companyName="Unknown" productName="Unnamed" productVersion="1" creationDateTime="2023-09-14T08:06:45"/>
  <contentHeader name="PlainProject" modificationDateTime="2023-09-14T08:09:26">
    <coordinateInfo>
      <fbd><scaling x="0" y="0"/></fbd>
      <ld><scaling x="0" y="0"/></ld>
      <sfc><scaling x="0" y="0"/></sfc>
    </coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes/>
    <pous>
      <pou name="program0" pouType="program" globalId="53fa6da4-a809-4ea1-892b-5413ac469989">
        <interface>
          <localVars constant="true" retain="false" nonretain="false" persistent="false" nonpersistent="false">
            <variable name="{var1_name}" globalId="UUID_b8f13c34-bc28-411c-9ab2-306eb932762a">
              <type><BOOL/></type>
              <documentation/>
            </variable>
            <variable name="{var2_name}" globalId="UUID_5921fee2-8062-4571-ba17-2ae95f496eef">
              <type><BOOL/></type>
              <documentation/>
            </variable>
          </localVars>
        </interface>
        <body>
          <ST>
            <xhtml:p xmlns:xhtml="http://www.w3.org/1999/xhtml">{var2_name} := {var1_name};</xhtml:p>
          </ST>
        </body>
        <documentation/>
      </pou>
    </pous>
  </types>
  <instances>
    <configurations>
      <configuration name="config" globalId="06f59f42-338e-411c-8316-bbfb45c687ea">
        <resource name="resource1">
          <task name="task0" interval="T#20ms" priority="0">
            <pouInstance name="instance0" typeName="program0">
              <addData>
                <data name="transmitterSettings">{{'interval': 1000}}</data>
              </addData>
            </pouInstance>
          </task>
          <globalVars constant="false" retain="false" nonretain="false" persistent="false" nonpersistent="false">
            <addData/>
            <documentation/>
          </globalVars>
          <addData>
            <data name="transmitterSettings">{{'interval': 1000}}</data>
          </addData>
        </resource>
      </configuration>
    </configurations>
  </instances>
  <addData>
    <data name="PROJECT_DOCS_ENSURED">true</data>
  </addData>
</project>
"""

    # Base templates for code_generation variations
    CODE_GEN_ERROR_LOG_TEMPLATE = """[18:16:53]: Building project...
[18:16:54]: Cannot build project.
[18:16:54]: Cannot build project.
stdout: Warning: PLC XML file doesn't follow XSD schema at line 43:
Element '{{http://www.plcopen.org/xml/tc6_0201}}data': Missing child element(s). Expected is one of ( {{*}}*, * ).Start build in /tmp/.tmpL3UKDb/build
Generating SoftPLC IEC-61131 ST/IL/SFC code...
Collecting data types
Collecting POUs
Generate POU program0

stderr: Traceback (most recent call last):
File "/root/beremiz/Beremiz_cli.py", line 130, in <module>
cli()
File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1130, in __call__
return self.main(*args, **kwargs)
File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1055, in main
rv = self.invoke(ctx)
File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1689, in invoke
return _process_result(rv)
File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1626, in _process_result
value = ctx.invoke(self._result_callback, value, **ctx.params)
File "/usr/local/lib/python3.10/dist-packages/click/decorators.py", line 84, in new_func
return ctx.invoke(f, obj, *args, **kwargs)
File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 760, in invoke
return self._callback(*args, **kwargs)
File "/root/beremiz/Beremiz_cli.py", line 110, in process_pipeline
ret = processor()
File "/root/beremiz/Beremiz_cli.py", line 74, in processor
return session.controller.build_project(target)
File "/root/beremiz/CLIController.py", line 59, in func_wrapper
return func(self, *args, **kwargs)
File "/root/beremiz/CLIController.py", line 137, in build_project
return 0 if self._Build() else 1
File "/root/beremiz/ProjectController.py", line 1749, in _Build
IECGenRes = self._Generate_SoftPLC()
File "/root/beremiz/ProjectController.py", line 794, in _Generate_SoftPLC
if self._Generate_PLC_ST():
File "/root/beremiz/ProjectController.py", line 810, in _Generate_PLC_ST
_program, errors, warnings = self.GenerateProgram(
File "/root/beremiz/PLCControler.py", line 453, in GenerateProgram
self.ProgramChunks = GenerateCurrentProgram(self, self.Project, errors, warnings,**kwargs)
File "/root/beremiz/PLCGenerator.py", line 1779, in GenerateCurrentProgram
generator.GenerateProgram(log,**kwargs)
File "/root/beremiz/PLCGenerator.py", line 482, in GenerateProgram
self.GeneratePouProgram(pou_name)
File "/root/beremiz/PLCGenerator.py", line 260, in GeneratePouProgram
program = pou_program.GenerateProgram(pou)
File "/root/beremiz/PLCGenerator.py", line 1728, in GenerateProgram
self.ComputeProgram(pou)
File "/root/beremiz/PLCGenerator.py", line 959, in ComputeProgram
self.ParentGenerator.GeneratePouProgramInText(text.upper())
AttributeError: 'NoneType' object has no attribute 'upper'
"""

    EMPTY_PROJECT_XML_TEMPLATE = """<project xmlns="http://www.plcopen.org/xml/tc6_0201">
  <fileHeader companyName="Unknown" productName="Unnamed" productVersion="1" creationDateTime="2023-09-14T08:06:45"/>
  <contentHeader name="PlainProject" modificationDateTime="2023-09-14T08:09:26">
    <coordinateInfo>
      <fbd><scaling x="0" y="0"/></fbd>
      <ld><scaling x="0" y="0"/></ld>
      <sfc><scaling x="0" y="0"/></sfc>
    </coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes/>
    <pous>
      <pou name="program0" pouType="program" globalId="b820c303-d3d8-4ec4-b9dc-ad9b0899448e">
        <interface>
          <localVars constant="false" retain="false" nonretain="false" persistent="false" nonpersistent="false"/>
        </interface>
        <body>
          <ST>
            <xhtml:p xmlns:xhtml="http://www.w3.org/1999/xhtml">{content}</xhtml:p>
          </ST>
        </body>
        <documentation/>
      </pou>
    </pous>
  </types>
  <instances>
    <configurations>
      <configuration name="config" globalId="1db0610b-0ca6-448d-8707-fd04476e237f">
        <resource name="resource1">
          <task name="task0" interval="T#20ms" priority="0">
            <pouInstance name="instance0" typeName="program0"/>
          </task>
        </resource>
      </configuration>
    </configurations>
  </instances>
  <addData>
    <data name="PROJECT_DOCS_ENSURED">true</data>
  </addData>
</project>
"""

    # Variable name pairs for constant error variations
    VAR_PAIRS = [
        ("InputSignal", "OutputSignal"),
        ("SensorValue", "ActuatorCommand"),
        ("Temperature", "SetPoint"),
        ("Pressure", "Relief"),
        ("Counter", "MaxCount"),
        ("Status", "State"),
        ("Flag", "Trigger"),
        ("SourceData", "TargetData"),
    ]

    @staticmethod
    def generate_constant_errors(count: int = 10) -> List[SyntheticError]:
        """Generate constant_error variations."""
        errors = []
        line_numbers = range(20, 80, 3)  # Different line numbers
        
        for i, line_num in enumerate(list(line_numbers)[:count]):
            var1, var2 = ErrorGenerator.VAR_PAIRS[i % len(ErrorGenerator.VAR_PAIRS)]
            
            # Format line with proper spacing
            line_formatted = f"{line_num:04d}:"
            assignment = f"{var2} := {var1};"
            
            log = ErrorGenerator.CONSTANT_ERROR_LOG_TEMPLATE.format(
                line=line_num,
                line_formatted=line_formatted,
                assignment=assignment
            )
            
            xml = ErrorGenerator.CONSTANT_ERROR_XML_TEMPLATE.format(
                var1_name=var1,
                var2_name=var2
            )
            
            errors.append(SyntheticError(
                log_text=log,
                xml_content=xml,
                expected_stage="iec_compilation",
                expected_severity="blocking",
                expected_complexity="trivial",
                error_type="constant_error"
            ))
        
        return errors

    @staticmethod
    def generate_code_generation_errors(count: int = 10) -> List[SyntheticError]:
        """Generate code_generation error variations."""
        errors = []
        
        for i in range(count):
            # Vary the content slightly or keep empty
            content = "" if i % 2 == 0 else "  "  # Some with empty, some with spaces
            
            log = ErrorGenerator.CODE_GEN_ERROR_LOG_TEMPLATE
            xml = ErrorGenerator.EMPTY_PROJECT_XML_TEMPLATE.format(content=content)
            
            errors.append(SyntheticError(
                log_text=log,
                xml_content=xml,
                expected_stage="code_generation",
                expected_severity="blocking",
                expected_complexity="trivial",
                error_type="code_generation"
            ))
        
        return errors

    @staticmethod
    def generate_all_test_cases(constant_error_count: int = 15, 
                               code_gen_count: int = 15) -> List[SyntheticError]:
        """Generate all test cases (20-30 total)."""
        errors = []
        errors.extend(ErrorGenerator.generate_constant_errors(constant_error_count))
        errors.extend(ErrorGenerator.generate_code_generation_errors(code_gen_count))
        random.shuffle(errors)
        return errors
