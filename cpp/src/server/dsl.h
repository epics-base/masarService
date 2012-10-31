/* dsl.h */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * EPICS pvDataCPP is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 *
 * This defines the interface that the Data Source Layer must implement.
 */
/* Author Marty Kraimer 2011.11 */

#ifndef DSL_H
#define DSL_H

#include <string>
#include <stdexcept>

#include <pv/noDefaultMethods.h>
#include <pv/pvData.h>
#include <pv/destroyable.h>


namespace epics { namespace masar{

class DSL;
typedef std::tr1::shared_ptr<DSL> DSLPtr;
/**
 * DSL - Data Source Layer
 * This is the interface that the Data Source Layer must implement
 */
class DSL :
    public epics::pvData::Destroyable,
    private epics::pvData::NoDefaultMethods

{
public:
    POINTER_DEFINITIONS(DSL)
    /**
     * Called by service layer to access the database.
     * @param pvArgument The argument which must follow the argument standard
     * for the masarService
     * @return An NTTable which has the results.
     */
    virtual epics::pvData::PVStructure::shared_pointer request(
        epics::pvData::String function,
        int num,
        epics::pvData::StringArray const &names,
        epics::pvData::StringArray const &values) = 0;
};

}}
#endif  /* DSL_H */


