from drozer.modules import common, Module


class Info(Module, common.Filters, common.PackageManager):
    name = "Get App Info"
    description = ""
    examples = ""
    author = "Dubu qingfeng"
    date = "2016-06-06"
    license = "BSD (3-clause)"
    path = ["ex", "app"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("-p", "--package", default=None, help="The Package Name")

    def execute(self, arguments):
        if arguments.package is None:
            for package in self.packageManager().getPackages(common.PackageManager.GET_ACTIVITIES):
                self.stdout.write("Package: %s\n" % package.packageName)
                self.__get_activities(arguments, package)
                self.__get_services(arguments, package)
                self.__get_receivers(arguments, package)
                self.__get_providers(arguments, package)

        else:
            package = self.packageManager().getPackageInfo(arguments.package, common.PackageManager.GET_ACTIVITIES)
            self.stdout.write("Package: %s\n" % package.packageName)
            self.__get_activities(arguments, package)
            self.__get_services(arguments, package)
            self.__get_receivers(arguments, package)
            self.__get_providers(arguments, package)

    def __get_providers(self, arguments, package):
        exported_providers = self.match_filter(package.providers, 'exported', True)
        if len(exported_providers) > 0:
            for provider in exported_providers:
                for authority in provider.authority.split(";"):
                    self.__print_provider(provider, authority, "  ")
        else:
            self.stdout.write(" No exported providers.\n\n")

    def __print_provider(self, provider, authority, prefix):
        self.stdout.write("%sAuthority: %s\n" % (prefix, authority))
        self.stdout.write("%s  Read Permission: %s\n" % (prefix, provider.readPermission))
        self.stdout.write("%s  Write Permission: %s\n" % (prefix, provider.writePermission))
        self.stdout.write("%s  Content Provider: %s\n" % (prefix, provider.name))
        self.stdout.write("%s  Multiprocess Allowed: %s\n" % (prefix, provider.multiprocess))
        self.stdout.write("%s  Grant Uri Permissions: %s\n" % (prefix, provider.grantUriPermissions))
        if provider.uriPermissionPatterns is not None:
            self.stdout.write("%s  Uri Permission Patterns:\n" % prefix)
            for pattern in provider.uriPermissionPatterns:
                self.stdout.write("%s    Path: %s\n" % (prefix, pattern.getPath()))
                self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[int(pattern.getType())]))
        if provider.pathPermissions is not None:
            self.stdout.write("%s  Path Permissions:\n" % prefix)
            for permission in provider.pathPermissions:
                self.stdout.write("%s    Path: %s\n" % (prefix, permission.getPath()))
                self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[int(permission.getType())]))
                self.stdout.write("%s      Read Permission: %s\n" % (prefix, permission.getReadPermission()))
                self.stdout.write("%s      Write Permission: %s\n" % (prefix, permission.getWritePermission()))

    def __get_receivers(self, arguments, package):
        exported_receivers = self.match_filter(package.receivers, 'exported', True)
        if len(exported_receivers) > 0:
            for receiver in exported_receivers:
                self.__print_receiver(receiver, "  ")
        else:
            self.stdout.write(" No exported receivers.\n\n")

    def __print_receiver(self, receiver, prefix):
        self.stdout.write("%s%s\n" % (prefix, receiver.name))
        self.stdout.write("%s  Permission: %s\n" % (prefix, receiver.permission))

    def __get_services(self, arguments, package):
        exported_services = self.match_filter(package.services, "exported", True)
        if len(exported_services) > 0:
            for service in exported_services:
                self.__print_service(service, "  ")
        else:
            self.stdout.write(" No exported services.\n\n")

    def __print_service(self, service, prefix):
        self.stdout.write("%s%s\n" % (prefix, service.name))
        self.stdout.write("%s  Permission: %s\n" % (prefix, service.permission))

    def __get_activities(self, arguments, package):
        exported_activities = self.match_filter(package.activities, 'exported', True)
        if len(exported_activities) > 0:
            for activity in exported_activities:
                self.__print_activity(package, activity, "    ")
        else:
            self.stdout.write(" No exported activities.\n\n")

    def __print_activity(self, package, activity, prefix):
        try:
            intent = self.new("android.content.Intent")
            comp = (package.packageName, activity.name)
            com = self.new("android.content.ComponentName", *comp)
            intent.setComponent(com)
            intent.setFlags(0x10000000)
            self.getContext().startActivity(intent)
        except Exception:
            self.stderr.write("%s need some premission." % activity.name)
        self.stdout.write("%s%s\n" % (prefix, activity.name))
        if activity._has_property("parentActivityName") and activity.parentActivityName is not None:
            self.stdout.write("%s  Parent Activity: %s\n" % (prefix, activity.parentActivityName))
        self.stdout.write("%s  Permission: %s\n" % (prefix, activity.permission))
        if activity.targetActivity is not None:
            self.stdout.write("%s  Target Activity: %s\n" % (prefix, activity.targetActivity))
