#include "vmlinux.h"
#include <udev-hid-bpf/hid_bpf.h>
#include <udev-hid-bpf/hid_bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define EF_VID 0x3746
#define R3PLUS_PID 0xFFFF

HID_BPF_CONFIG(HID_DEVICE(BUS_USB, HID_GROUP_GENERIC, EF_VID, R3PLUS_PID));

SEC(HID_BPF_RDESC_FIXUP)
int BPF_PROG(r3_plus_fix_rdesc, struct hid_bpf_ctx *hctx)
{
    // check that the fix hasn't already been applied
    const int expected_length = 376;
    if (hctx->size != expected_length)
        return 0;

    __u8 *data = hid_bpf_get_data(hctx, 0, 4096);
    if (!data)
        return 0;

    // append 3x 0xC0 to the report descriptor
    // because it is missing these three end collection bytes
    // this fixes a firmware bug known to be present in
    // river 3 plus FW V1.33.81.55
    data[expected_length] = 0xC0;
    data[expected_length + 1] = 0xC0;
    data[expected_length + 2] = 0xC0;

    return expected_length+3;
}

HID_BPF_OPS(fix_rd) = {
  .hid_rdesc_fixup = (void *)r3_plus_fix_rdesc,
};

char _license[] SEC("license") = "GPL";
