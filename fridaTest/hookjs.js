// Java.perform(function () {
// 	console.log("Start debugging");
//     var Activity = Java.use("android.app.Activity");
//     Activity.onResume.implementation = function () {
//         send("onResume got called! Let's call the original implementation");
//         this.onResume();
//     };
// });

// Process.enumerateModules({
//     onMatch: function(module) {
//         console.log(
//             "Module name: " +
//                 module.name +
//                 " - " +
//                 "Base Address: " +
//                 module.base.toString()
//         );
//     },
//     onComplete: function() {}
// });

Java.perform(function() {
    var LibBili = Java.use("com.bilibili.nativelibrary.LibBili");
    var SortedMap = Java.use("java.util.SortedMap");
	var MapNode = Java.use("java.util.Map$Entry");
	var J_String = Java.use("java.lang.String");

    LibBili.s.overload("java.util.SortedMap").implementation = function() {
        var arg = arguments[0];
        var iterator = Java.cast(arg, SortedMap)
            .entrySet()
            .iterator();
        var logData = {};
        while (iterator.hasNext()) {
            var entry = Java.cast(iterator.next(), MapNode);
            logData[entry.getKey()] = Java.cast(entry.getValue(), J_String).toString();
        }
        console.log("bili.s arg: " + JSON.stringify(logData));
        var ret = this.s(arg); // ret is Lcom/bilibili/nativelibrary/SignedQuery;
        console.log("bili.s ret: " + ret);
        return ret;
    };
});

// var nativePointer = Module.findExportByName("libbili.so","s");
// send("gif native pointers:"+nativePointer)
// Interceptor.attach(nativePointer,{
// 	onLeave:function(retval){
// 		send("gifcore so result value: "+retval)
// 		return retval
// 	}
// })
