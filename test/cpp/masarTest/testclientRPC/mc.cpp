#include <pv/event.h>

#include <pv/clientFactory.h>
#include <pv/rpcClient.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;



class RequesterImpl : public Requester,
     public std::tr1::enable_shared_from_this<RequesterImpl>
{
public:

    virtual string getRequesterName()
    {
        return "RequesterImpl";
    };

    virtual void message(string const & message,MessageType messageType)
    {
        std::cout << "[" << getRequesterName() << "] message(" << message << ", " << getMessageTypeName(messageType) << ")" << std::endl;
    }
};



int main()
{
  ClientFactory::start();

  Requester::shared_pointer requester(new RequesterImpl());
  PVStructure::shared_pointer pvRequest =
         getCreateRequest()->createRequest("", requester);

int cc = 0;
while (1)
{
  RPCClient::shared_pointer client(RPCClient::create("masarService4Test", pvRequest));
  client->issueConnect();
  if (!client->waitConnect(1.0))
  {
    std::cerr << "failed to connect: " << client->getMessage() << std::endl;
    return -1;
  }

  FieldCreatePtr fieldCreate = getFieldCreate();
 
  StringArray fieldNames;
  fieldNames.push_back("function");
  fieldNames.push_back("eventid");

  FieldConstPtrArray fields;
  fields.push_back(fieldCreate->createScalar(pvString));
  fields.push_back(fieldCreate->createScalar(pvString));

  PVStructure::shared_pointer args(getPVDataCreate()->createPVStructure(fieldCreate->createStructure(fieldNames, fields))); 
  args->getStringField("function")->put("retrieveSnapshot");
  args->getStringField("eventid")->put("1005");

  client->issueRequest(args, false);
  PVStructure::shared_pointer result = client->waitRequest();
  if (!result)
  {
    std::cerr << "null result: " << client->getMessage() << std::endl;
    return -1;
  }
  else
//    std::cout << *result << std::endl;
    std::cout << (++cc) << std::endl;
  client->destroy();
} 

  return 0;
}
