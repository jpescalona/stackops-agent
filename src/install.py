
import sys
import platform
import multiprocessing
import os
import commands

import utils
import StackOps
import StackOpssubs

from socket import gethostname; 


class Machine:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    def getCPUType(self):
        return os.popen2("cat /proc/cpuinfo | grep 'model name' | sed 's/\(.*\): //g'")[1].read().splitlines()

    def getMachine(self):
        return platform.machine()

    def getCPUCount(self):
        return multiprocessing.cpu_count()

    def getCPUSpeed(self):
        return os.popen2("cat /proc/cpuinfo | grep 'cpu MHz' | sed 's/[^0-9\.]//g'")[1].read().splitlines()

    def getMemoryAvailable(self):
        return 1024 * int(os.popen2("cat /proc/meminfo | grep 'MemTotal' | sed 's/[^0-9\.]//g'")[1].read())

    def getVirtualization(self):
        iface =  os.popen2("egrep '(vmxx|svmx)' /proc/cpuinfo")[1].read()
        if len(iface)>0:
            return "True"
        else:
            return "False"

    def getIfaceList(self):
        ifaces =  os.popen2("cat /proc/net/dev | sed 's/:\(.*\)//g'")[1].read().splitlines()
        del ifaces [0]
        del ifaces [0]
        ifaces_list=[]
        for x in ifaces:
            y = x.strip()
            if (y!="lo"):
                ifaceUp = os.popen2("ifconfig | grep " + y )[1].read()
                if len(ifaceUp)>0:
                    ifaces_list.append(y)
        return ifaces_list

    def getIfaceVendorList(self,iface):
        vendor =  os.popen2("lshw -short -c network | grep '" + iface + "'")[1].read()[43:].strip("\n")
        return vendor

    def getBlockDeviceList(self):
        mnt = commands.getoutput("mount -v")
        lines = mnt.split('\n')
        inf = []
        for line in lines:
            dev = {}
            device = line.split()[0]
            mountpoint = line.split()[2]
            if (device!="none"):
                dev['mountpoint']=mountpoint
                dev['device']=device
                try:
                    s = os.statvfs(line.split()[2])
                    dev['size'] = s.f_bsize * s.f_blocks
                    dev['used'] = s.f_bsize * (s.f_blocks - s.f_bavail)
                except OSError:
                    print 'OSError'
                inf.append(dev)
        return inf

class OperatingSystem(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def getUname(self):
        uname = platform.uname()
        return uname[0] + "/" + uname [1] + "/" + uname [2] + "/" + uname [3] + "/" + uname [4]+ "/" + uname [5]
    
    def getHostname(self):
        return gethostname()
    
    def getNameservers(self):
        mnt = commands.getstatusoutput("cat /etc/resolv.conf")
        if (mnt[0]>0):
            raise Exception(mnt[1])
        lines = mnt[1].split('\n')
        inf = set([])
        for line in lines:
            if (line.startswith("nameserver")):
                inf.add(line.split(" ")[1])
        return inf
        
    def getNetworkConfiguration(self):
        machine = Machine()
        inf = []        
        mnt = commands.getstatusoutput("cat /etc/network/interfaces")
#        mnt = commands.getstatusoutput("cat interfaces")
        if (mnt[0]>0):
            raise Exception(mnt[1])
        devnets = mnt[1].split('auto')
        for devnet in devnets:
            net = devnet.split('\n')
            dev = {}
            for e in net:
                element = e.strip()
                if (element in machine.getIfaceList()):
                    params = element.split(' ')
#                    if (params[0] == 'iface'):
#                        dev['interface'] = params[1]
                    dev['name'] = element
                    dev['dhcp'] = "true"
                    if (element.endswith('dhcp')):
                        dev['dhcp'] = "true"
                    if (element.endswith('static')):
                        dev['dhcp'] = "false" 
                    if (params[0] == 'address'):
                        dev['address'] =  params[1]
                    else:
                        dev['address'] = "none"                         
                    if (params[0] == 'netmask'):
                        dev['netmask'] =  params[1]
                    else:
                        dev['netmask'] = "none"                         
                    if (params[0] == 'gateway'):
                        dev['gateway'] =  params[1]                    
                    else:
                        dev['gateway'] = "none"
                    dev['default'] = "false"
                    dev['virtual'] = "false"                                             
            if (len(dev)>0):
                inf.append(dev)
        return inf
                
class Filler(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        
    def populateCPU(self, name, speed, cores):
        cpu = StackOps.cpu()
        cpu.set_cores(cores)
        cpu.set_speed(speed)
        cpu.set_name(name)
        return cpu

    def populateCPUs(self, cpu_list):
        cpus = StackOps.cpus()
        for cpu in cpu_list:
            cpus.add_cpu(cpu)
        return cpus
    
    def populateNIC(self, interface, type_, name):
        nic = StackOps.nic()
        nic.set_interface(interface)
        nic.set_type(type_)
        nic.set_name(name)
        return nic
    
    def populateNICs(self, nic_list):
        nics = StackOps.nics()
        for nic in nic_list:
            nics.add_nic(nic)
        return nics

    def populatePartition(self, mountpoint, device, size, used):
        partition = StackOps.partition()
        partition.set_mountpoint(mountpoint)
        partition.set_device(device)
        partition.set_size(size)
        partition.set_used(used)
        return partition
    
    def populatePartitions(self, partition_list):
        partitions = StackOps.partitions()
        for partition in partition_list:
            partitions.add_partition(partition)
        return partitions
    
    def populateHardware(self, cpus, memory, nics, virtualization, partitions):
        hardware = StackOps.hardware()
        hardware.set_memory(memory)
        hardware.set_cpus(cpus)
        hardware.set_virtualization(virtualization)
        hardware.set_nics(nics)
        hardware.set_partitions(partitions)
        return hardware

    def populateIface(self, address, default, dhcp, gateway, name, netmask,virtual):
        iface = StackOps.iface()
        iface.set_address(address)
        iface.set_default(default)
        iface.set_dhcp(dhcp)
        iface.set_gateway(gateway)
        iface.set_name(name)
        iface.set_netmask(netmask)
        iface.set_virtual(virtual)
        return iface
    
    def populateNetwork(self, hostname, nameserver_list, iface_list):
        network = StackOps.network()
        network.set_hostname(hostname)
        print nameserver_list
        for nameserver in nameserver_list:
            network.add_nameserver(nameserver)
        for iface in iface_list:
            address = iface["address"]
            default = iface["default"]
            dhcp = iface["dhcp"]
            gateway = iface["gateway"]
            name = iface["name"]
            netmask = iface["netmask"]
            virtual = iface["virtual"]
            network.add_iface(self.populateIface(address, default, dhcp, gateway, name, netmask,virtual))
        return network
        
    def populateOS(self, uname, network):
        os = StackOps.os()
        os.set_uname(uname)
        os.set_network(network)
        return os

    def populateSoftware(self, os):
        software = StackOps.software()
        software.set_os(os)
        return software


    def populateSqlConnection(self, username, password, hostname, port, schema):
        sql_connection = StackOps.service()
        sql_connection.set_type('sql_connection')
        mysql_username = StackOps.property()
        mysql_username.set_name('username')
        mysql_username.set_value(username)
        sql_connection.add_property(mysql_username)
        mysql_pass = StackOps.property()
        mysql_pass.set_name('password')
        mysql_pass.set_value(password)
        sql_connection.add_property(mysql_pass)
        mysql_host = StackOps.property()
        mysql_host.set_name('host')
        mysql_host.set_value(hostname)
        sql_connection.add_property(mysql_host)
        mysql_port = StackOps.property()
        mysql_port.set_name('port')
        mysql_port.set_value(port)
        sql_connection.add_property(mysql_port)
        mysql_schema = StackOps.property()
        mysql_schema.set_name('schema')
        mysql_schema.set_value(schema)
        sql_connection.add_property(mysql_schema)
        return sql_connection

    def populateS3Host(self, controller_host):
        s3_host = StackOps.service()
        s3_host.set_type('s3_host')
        host = StackOps.property()
        host.set_name('hostname')
        host.set_value(controller_host)
        s3_host.add_property(host)
        return s3_host

    def populateMomHost(self, controller_host):
        mom_host = StackOps.service()
        mom_host.set_type('rabbit_host')
        host = StackOps.property()
        host.set_name('hostname')
        host.set_value(controller_host)
        mom_host.add_property(host)
        return mom_host

    def populateControllerHost(self, controller_host):
        cc_host = StackOps.service()
        cc_host.set_type('cc_host')
        host = StackOps.property()
        host.set_name('hostname')
        host.set_value(controller_host)
        cc_host.add_property(host)
        return cc_host

    def populateVerbose(self):
        verbose = StackOps.service()
        verbose.set_type('verbose')
        return verbose

    def populateEc2Url(self, hostname, port, uri):
        ec2url = StackOps.service()
        ec2url.set_type('ec2_url')
        ec2url_host = StackOps.property()
        ec2url_host.set_name('host')
        ec2url_host.set_value(hostname)
        ec2url.add_property(ec2url_host)
        ec2url_port = StackOps.property()
        ec2url_port.set_name('port')
        ec2url_port.set_value(port)
        ec2url.add_property(ec2url_port)
        ec2url_uri = StackOps.property()
        ec2url_uri.set_name('uri')
        ec2url_uri.set_value(uri)
        ec2url.add_property(ec2url_uri)
        return ec2url
    
    def populateNetworkManager(self,type,fixed_range,network_size):
        network = StackOps.service()
        network.set_type('network_manager')

        type_network = StackOps.property()
        type_network.set_name('type')
        type_network.set_value(type)
        network.add_property(type_network)

        fixed_range_network = StackOps.property()
        fixed_range_network.set_name('fixed_range')
        fixed_range_network.set_value(fixed_range)
        network.add_property(fixed_range_network)

        network_size_network = StackOps.property()
        network_size_network.set_name('network_size')
        network_size_network.set_value(network_size)
        network.add_property(network_size_network)
        return network

    def populateController(self, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, controller_host, ec2_url_port, ec2_url_uri,network_type,network_fixed_range,network_size):
        controller = StackOps.component()
        controller.set_name('controller')
        
        sql_connection = self.populateSqlConnection(mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema)
        controller.add_service(sql_connection)
        
        s3_host = self.populateS3Host(controller_host)
        controller.add_service(s3_host)

        mom_host = self.populateMomHost(controller_host)
        controller.add_service(mom_host)

        cc_host = self.populateControllerHost(controller_host)
        controller.add_service(cc_host)

        verbose = self.populateVerbose()
        controller.add_service(verbose)

        ec2_url = self.populateEc2Url(controller_host,ec2_url_port,ec2_url_uri)
        controller.add_service(ec2_url)

        network_manager = self.populateNetworkManager(network_type,network_fixed_range,network_size)
        controller.add_service(network_manager)

        return controller
        
    def populateCloud(self, cloud, component, topology):
        if (cloud is None):
            cloud = StackOps.cloud()
        if (component is not None):
            cloud.add_component(component)
        if (topology is not None):
            cloud.set_topology(topology)
        return cloud

    def populateNode(self, hardware, software,cloud):
        node = StackOps.node()
        node.set_hardware(hardware)
        node.set_software(software)
        node.set_cloud(cloud)
        return node
    
    def getPropertyValue(self,component,service_name,property_name):
        for i in component.get_service():
            if (i.get_type()==service_name):
                for j in i.get_property():
                    if (j.get_name()==property_name):
                        return j.get_value()
        return ''            

    def createNode(self,cloud):
        
        machine = Machine()
        operatingsystem = OperatingSystem()
        
        # CPU Info
        type_list = machine.getCPUType()
        speed_list = machine.getCPUSpeed()
        cpu_list = []
        for name, speed in map(None, type_list, speed_list):
            cpu_list.append(self.populateCPU(name, int(speed.split(".")[0]), 1))
        cpus = self.populateCPUs(cpu_list)
        
        # Memory
        memory = machine.getMemoryAvailable()
        
        # Network
        nic_list = []
        iface_list = machine.getIfaceList()
        for iface in iface_list:
            nic_list.append(self.populateNIC(iface, "", machine.getIfaceVendorList(iface)))
        nics = self.populateNICs(nic_list)

        # Partitions
        partition_list = []
        blockdev_list = machine.getBlockDeviceList()
        for blockdev in blockdev_list:
            partition_list.append(self.populatePartition(blockdev["mountpoint"], blockdev["device"], blockdev["size"], blockdev["used"]))
        partitions = self.populatePartitions(partition_list)
        
        # Hardware information
        hardware = self.populateHardware(cpus, memory, nics, machine.getVirtualization(), partitions)

        # OS information
        # uname description
        uname = operatingsystem.getUname()
        
        # network configuration
        hostname = operatingsystem.getHostname()
        nameserver_list = operatingsystem.getNameservers()
        iface_list = operatingsystem.getNetworkConfiguration()
        network = self.populateNetwork(hostname, nameserver_list, iface_list)
        os = self.populateOS(uname, network)
        
        # Software information
        software = self.populateSoftware(os)
        
        # Cloud components
        if (cloud is None):
            cloud = StackOps.cloud()
            
        # Node information
        node = self.populateNode(hardware, software, cloud)
        node.export(sys.stdout, 0)
        
        return node

    def importNode(self,xml):
        node = StackOpssubs.parse(xml)
        # Only Cloud is relevant
        return node.get_cloud()
    
class Package:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    def install_common(self):
        
        utils.execute(self.install_cmd())
        
    def install_cmd(self):
        """Builds apt-get install command"""
        cmd = ['sudo apt-get install -y',
               ' rabbitmq']
#               ' --bind-interfaces',
#               ' --conf-file=',
#               ' --pid-file=%s' % _dhcp_file(net['bridge'], 'pid'),
#               ' --listen-address=%s' % net['gateway'],
#               ' --except-interface=lo',
#               ' --dhcp-range=%s,static,120s' % net['dhcp_start'],
#               ' --dhcp-hostsfile=%s' % _dhcp_file(net['bridge'], 'conf'),
#               ' --dhcp-script=%s' % FLAGS.dhcpbridge,
#               ' --leasefile-ro']
        return ''.join(cmd)
    
   