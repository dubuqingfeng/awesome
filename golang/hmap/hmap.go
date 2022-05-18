package hmap

import (
    "hash/fnv"
    "unsafe"
)

type _key string

type _val unsafe.Pointer

func (v _val) set(val string) {
    v = unsafe.Pointer(&val)
}

func (v _val) get() string {
    return *(*string)(unsafe.Pointer(&v))
}

type _entry struct {
    key *_key
    val *_val
}

func (e *_entry) set(val string) {
    // implement set
}

func (e *_entry) get() (string, bool) {
    // implement get
    return "", false
}

func (e *_entry) del() {
    // implement del
}

type _bucket struct {
    entries []*_entry
}

func newbucket() *_bucket {
    return &_bucket{ make([]*_entry, 8) }
}

func (b *_bucket) entry(lob uint, hob uint) *_entry {
    // implement finding correct entry
    return nil
}

func addbuckets() []*_bucket {
    buckets := make([]*_bucket, 8)
    for _, bucket := range buckets {
        buckets = append(buckets, newbucket())
    }
    return buckets
}

type hmap struct {
    buckets []*_bucket
}

func NewMap() *hmap {
    return &hmap{ addbuckets() }
}

func (h *hmap) hash(key string) (*_bucket, uint, uint) {
    hc := fnv.New32()
    hc.Write(key)
    bucket := uint(hc.Sum32()) % uint(len(h.buckets))
    lob17 := bucket & 0x1FFFF
    hob17 := (bucket & (0x1FFFF << (32 - 17))) >> (32 - 17)
    return (*h).buckets[bucket], lob17, hob17
}

func (h *hmap) Set(key string, val string) {
    // implememt set
    buk, hob, lob := h.hash(key)
    ent := buk.entry(hob, lob)
    ent.set(val)
}

func (h *hmap) Get(key string) (string, bool){
    // implement get
    buk, hob, lob := h.hash(key)
    ent := buk.entry(hob, lob)
    return ent.get()
}

func (h *hmap) Del(key string) {
    // implement del
    buk, hob, lob := h.hash(key)
    ent := buk.entry(hob, lob)
    ent.del()
}
