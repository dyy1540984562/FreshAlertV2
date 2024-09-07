"use client"

import { useState, useEffect, useRef } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent } from "@/components/ui/sheet"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { FoodService } from "@/services/foodService"
import { AuthService } from "@/services/authService"
import { Food, User } from "@/types"
import { SearchIcon as SearchIconImport, TrashIcon as TrashIconImport } from "@/components/icons"
import { Alert } from "@/components/Alert"
import md5 from 'js-md5';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"

export function Component() {
  const [open, setOpen] = useState(false)
  const [foods, setFoods] = useState<Food[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [newFoodName, setNewFoodName] = useState("")
  const [newProductionDate, setNewProductionDate] = useState("")
  const [newShelfLife, setNewShelfLife] = useState("")
  const [user, setUser] = useState<User | null>(null)
  const [showLogin, setShowLogin] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [imageFile, setImageFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showUserManagement, setShowUserManagement] = useState(false)
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordError, setPasswordError] = useState("")
  const [secretKeyProvider, setSecretKeyProvider] = useState("kimi")
  const [secretKey, setSecretKey] = useState("")
  const [alertMessage, setAlertMessage] = useState<{ type: 'error' | 'success', message: string } | null>(null)

  useEffect(() => {
    if (user) {
      fetchFoods()
    } else {
      setFoods([])
    }
  }, [user])

  const fetchFoods = async () => {
    if (!user) return
    try {
      const fetchedFoods = await FoodService.getFoods(user.id)
      setFoods(fetchedFoods)
    } catch (error) {
      showError(error instanceof Error ? error.message : 'An unknown error occurred')
    }
  }

  const filteredFoods = foods.filter((food) => 
    food.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const showError = (message: string) => {
    setAlertMessage({ type: 'error', message });
  }

  const showSucc = (message: string) => {
    setAlertMessage({ type: 'error', message });
  }

  const showMessage = (type: 'error' | 'success', message: string) => {
    setAlertMessage({ type, message });
  }

  const handleDelete = async (id: number) => {
    if (!user) return
    try {
      await FoodService.deleteFood(id, user.id)
      setFoods(foods.filter((food) => food.id !== id))
    } catch (error) {
      showError(error instanceof Error ? error.message : 'An unknown error occurred')
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImageFile(file);
      recognizeFood(file);
    }
  };

  const recognizeFood = async (file: File) => {
    if (!user) return; // 确保用户已登录
    try {
      const formData = new FormData();
      formData.append('image', file);
      const recognizedFood = await FoodService.recognizeFood(formData, user.id);
      if (recognizedFood.name) setNewFoodName(recognizedFood.name);
      if (recognizedFood.productionDate) {
        const productionDate = new Date(recognizedFood.productionDate).toISOString().split('T')[0];
        setNewProductionDate(productionDate);
      }
      if (recognizedFood.shelfLife) {
        setNewShelfLife(recognizedFood.shelfLife.toString());
      }
      if (!recognizedFood.name && !recognizedFood.productionDate && !recognizedFood.shelfLife) {
        showError('食物识别失败: 无法识别出食物名称、生产日期保质期');
      }
    } catch (error) {
      console.error('Error:', error);
      showError('食物识别失败: ' + (error instanceof Error ? error.message : String(error)));
    }
  };

  const handleAddFood = async () => {
    if (!user) return
    try {
      const formData = new FormData();
      formData.append('name', newFoodName);
      formData.append('productionDate', newProductionDate);
      formData.append('shelfLife', newShelfLife);
      formData.append('userId', user.id.toString());
      if (imageFile) {
        formData.append('image', imageFile);
      }

      const addedFood = await FoodService.addFood(formData);
      setFoods([...foods, addedFood]);
      setOpen(false);
      setNewFoodName("");
      setNewProductionDate("");
      setNewShelfLife("");
      setImageFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      showError(error instanceof Error ? error.message : '添加食物时发生未知错误');
    }
  }

  const handleLogin = async () => {
    try {
      const hashedPassword = md5(password);
      const userData = await AuthService.login(username, hashedPassword);
      setUser(userData);
      setShowLogin(false);
      setUsername("");
      setPassword("");
    } catch (error) {
      showError(error instanceof Error ? error.message : '登录时发生未知错误');
    }
  }

  const handleRegister = async () => {
    try {
      const hashedPassword = md5(password);
      const userData = await AuthService.register(username, hashedPassword);
      setUser(userData);
      setShowRegister(false);
      setUsername("");
      setPassword("");
    } catch (error) {
      showError(error instanceof Error ? error.message : '注册时发生未知错误');
    }
  }

  const handleLogout = () => {
    setUser(null)
    setFoods([])
  }

  const handleChangePassword = async () => {
    if (!user) return
    try {
      if (!newPassword) {
        setPasswordError('密码不能为空');
        return;
      }
      if (newPassword !== confirmPassword) {
        setPasswordError('两次输入的密码不一致');
        return;
      }
      setPasswordError('');
      await AuthService.changePassword(user.id, md5(newPassword))
      showSucc('密码修改成功')
      setNewPassword("")
      setConfirmPassword("")
    } catch (error) {
      showError(error instanceof Error ? error.message : '修改密码时发生未知错误')
    }
  }

  const handleAddSecretKey = async () => {
    if (!user) return
    try {
      await AuthService.addSecretKey(user.id, secretKeyProvider, secretKey)
      showMessage('success', 'Secret Key 添加成功')
      setSecretKey("")
    } catch (error) {
      showMessage('error', error instanceof Error ? error.message : '添加 Secret Key 时发生未知错误')
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6 relative">
      <div className="absolute top-4 right-4 flex gap-2">
        {user ? (
          <>
            <span>欢迎, {user.username}!</span>
            <Button onClick={() => setShowUserManagement(true)}>用户管理</Button>
            <Button onClick={handleLogout}>登出</Button>
          </>
        ) : (
          <>
            <Button onClick={() => setShowLogin(true)}>登录</Button>
            <Button onClick={() => setShowRegister(true)}>注册</Button>
          </>
        )}
      </div>
      <h1 className="text-2xl font-bold mb-6">食物过期管理</h1>
      {user ? (
        <>
          <div className="flex items-center mb-6">
            <div className="relative flex-1">
              <SearchIconImport className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="text"
                placeholder="搜索食物..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button onClick={() => setOpen(true)} className="ml-4">
              添加食物
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="bg-muted">
                  <th className="px-4 py-2 text-left">名称</th>
                  <th className="px-4 py-2 text-left">生产日期</th>
                  <th className="px-4 py-2 text-left">保质期(天)</th>
                  <th className="px-4 py-2 text-left">过期日期</th>
                  <th className="px-4 py-2 text-left">剩余天数</th>
                  <th className="px-4 py-2 text-right">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredFoods.map((food) => (
                  <tr 
                    key={food.id} 
                    style={{
                      backgroundColor: 
                        food.daysLeft < 0 ? '#FEE2E2' :
                        food.daysLeft < 7 ? '#FEE2E2' :
                        food.daysLeft < 30 ? '#FEF3C7' :
                        '#D1FAE5'
                    }}
                    className="border-b"
                  >
                    <td className="px-4 py-2">{food.name}</td>
                    <td className="px-4 py-2">{food.productionDate}</td>
                    <td className="px-4 py-2">{food.shelfLife}</td>
                    <td className="px-4 py-2">{food.expirationDate}</td>
                    <td className="px-4 py-2 font-bold" style={{
                      color: 
                        food.daysLeft < 0 ? '#DC2626' :
                        food.daysLeft < 7 ? '#EF4444' :
                        food.daysLeft < 30 ? '#F59E0B' :
                        '#10B981'
                    }}>
                      {food.daysLeft} 天
                    </td>
                    <td className="px-4 py-2 text-right">
                      <Button variant="outline" size="icon" onClick={() => handleDelete(food.id)}>
                        <TrashIconImport className="h-4 w-4" />
                        <span className="sr-only">删除</span>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetContent className="w-full max-w-md">
              <Card>
                <CardHeader>
                  <CardTitle>添加食物</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="foodImage">食物图片</Label>
                    <Input
                      id="foodImage"
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      ref={fileInputRef}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="name">食物名称</Label>
                    <Input
                      id="name"
                      value={newFoodName}
                      onChange={(e) => setNewFoodName(e.target.value)}
                      placeholder="输入食物名称"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="productionDate">生产日期</Label>
                    <Input
                      id="productionDate"
                      type="date"
                      value={newProductionDate}
                      onChange={(e) => setNewProductionDate(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="shelfLife">保质期(天)</Label>
                    <Input
                      id="shelfLife"
                      type="number"
                      value={newShelfLife}
                      onChange={(e) => setNewShelfLife(e.target.value)}
                      placeholder="输入保质期天数"
                    />
                  </div>
                </CardContent>
                <CardFooter className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setOpen(false)}>
                    取消
                  </Button>
                  <Button onClick={handleAddFood}>添加</Button>
                </CardFooter>
              </Card>
            </SheetContent>
          </Sheet>
          <Sheet open={showUserManagement} onOpenChange={setShowUserManagement}>
            <SheetContent className="w-full max-w-md sm:max-w-lg">
              <Card>
                <CardHeader>
                  <CardTitle>用户管理</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="new-password">新密码</Label>
                    <Input
                      id="new-password"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                    <Label htmlFor="confirm-password">确认新密码</Label>
                    <Input
                      id="confirm-password"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                    {passwordError && <p style={{ color: 'red' }}>{passwordError}</p>}
                    <Button onClick={handleChangePassword}>修改密码</Button>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="secret-key-provider">Secret Key 提供商</Label>
                    <Select value={secretKeyProvider} onValueChange={setSecretKeyProvider}>
                      <SelectItem value="kimi">Kimi</SelectItem>
                      {/* <SelectItem value="openai">OpenAI</SelectItem>
                      <SelectItem value="tongyi">通义</SelectItem> */}
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="secret-key">Secret Key</Label>
                    <Input
                      id="secret-key"
                      type="password"
                      value={secretKey}
                      onChange={(e) => setSecretKey(e.target.value)}
                    />
                    <Button onClick={handleAddSecretKey}>添加 Secret Key</Button>
                  </div>
                </CardContent>
              </Card>
            </SheetContent>
          </Sheet>
        </>
      ) : (
        <p className="text-center mt-16 text-2xl font-bold font-serif text-gray-600">
          请登录以管理您的食物信息。
        </p>
      )}

      {alertMessage && (
        <Alert
          type={alertMessage.type}
          title={alertMessage.type === 'error' ? '错误' : '成功'}
          message={alertMessage.message}
          onClose={() => setAlertMessage(null)}
        />
      )}

      <Sheet open={showLogin} onOpenChange={setShowLogin}>
        <SheetContent className="w-full max-w-md sm:max-w-lg">
          <Card>
            <CardHeader>
              <CardTitle>登录</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">用户名</Label>
                <Input
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={handleLogin}>登录</Button>
            </CardFooter>
          </Card>
        </SheetContent>
      </Sheet>

      <Sheet open={showRegister} onOpenChange={setShowRegister}>
        <SheetContent className="w-full max-w-md sm:max-w-lg">
          <Card>
            <CardHeader>
              <CardTitle>注册</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="reg-username">用户名</Label>
                <Input
                  id="reg-username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reg-password">密码</Label>
                <Input
                  id="reg-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={handleRegister}>注册</Button>
            </CardFooter>
          </Card>
        </SheetContent>
      </Sheet>
    </div>
  )
}