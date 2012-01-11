/* testCreateGather.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * EPICS pvDataCPP is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.01 */

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>

#include <pv/dslPY.h>

using namespace epics::pvData;
using namespace epics::masar;

static StructureConstPtr createStructure()
{
    FieldCreate *fieldCreate = getFieldCreate();
    ScalarArrayConstPtr propertyName = fieldCreate->createScalarArray("propertyName",pvString);
    ScalarArrayConstPtr propertyValue = fieldCreate->createScalarArray("propertyValue",pvString);
    ScalarConstPtr name = fieldCreate->createScalar("name",pvString);
    FieldConstPtrArray fields = new FieldConstPtr[3];
    fields[0] = name;
    fields[1] = propertyName;
    fields[2] = propertyValue;
    StructureConstPtr infoStruct = fieldCreate->createStructure("pvinfo",3,fields);
    StructureArrayConstPtr info = fieldCreate->createStructureArray("pvinfo",infoStruct);
    ScalarConstPtr npv = fieldCreate->createScalar("npv",pvInt);
    fields = new FieldConstPtr[2];
    fields[0] = npv;
    fields[1] = info;
    StructureConstPtr top = fieldCreate->createStructure(
        "result",2,fields);
    return top;
}


int main(int argc,char *argv[])
{
    DSL::shared_pointer dsl = createDSL_RDB();
    if(dsl.get()==0) {
        printf("createDSL failed\n");
        return -1;
    }
    String function("saveMasar");
    int num = 4;
    String names[num];
    names[0] = String("data");
    names[1] = String("servicename");
    names[2] = String("configname");
    names[3] = String("comment");
    String values[num];
    values[0] = String("pv_name,value,status,severity,timeStamp");
    values[1] = String("servicexxx");
    values[2] = String("configxxx");
    values[3] = String("this is a comment");
    PVStructure::shared_pointer result = dsl->request(
        function,num,names,values);
    if(result.get()==0) {
        printf("DSL::result failed\n");
        return -1;
    }
    String buf;
    result->toString(&buf);
    printf("result\n%s\n",buf.c_str());
    return (0);
}

